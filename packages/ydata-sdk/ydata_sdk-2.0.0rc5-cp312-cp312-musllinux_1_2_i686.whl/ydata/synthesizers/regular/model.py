"""Synthesizer model."""
from __future__ import annotations

from functools import partial
from os import getenv
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

from pandas import DataFrame as pdDataFrame
from pandas import to_numeric

from ydata.connectors.storages.big_query_connector import BigQueryConnector
from ydata.connectors.storages.object_storage_connector import ObjectStorageConnector
from ydata.connectors.storages.rdbms_connector import RDBMSConnector
from ydata.datascience.common import PrivacyLevel
from ydata.dataset import Dataset
from ydata.dataset.holdout import Holdout
from ydata.metadata.metadata import Metadata
from ydata.preprocessors.identity import Identity as IdentityPreprocessor
from ydata.preprocessors.methods.anonymization import AnonymizerConfigurationBuilder
from ydata.preprocessors.regular.preprocessor import SynthpopPreprocessor, SynthpopSegmentPreprocessor
from ydata.synthesizers.base_model import BaseModel, SegmentByType
from ydata.synthesizers.conditional import ConditionalFeature
from ydata.synthesizers.logger import synthlogger_config
from ydata.synthesizers.prototype import PipelinePrototype
from ydata.synthesizers.utils.models import RegularSynthesizerModel
from ydata.utils.data_types import DataType
from ydata.utils.misc import log_time_factory
from ydata.utils.random import RandomSeed

from ydata._licensing import synthesizer_sample

# Define here the logging status and definition
logger = synthlogger_config(verbose=getenv(
    "VERBOSE", "false").lower() == "true")


class RegularSynthesizer(BaseModel):
    # DataTypes that we are able to synthesize
    _SUPPORTED_DTYPES = [DataType.NUMERICAL, DataType.STR,
                         DataType.CATEGORICAL, DataType.DATE]

    def __init__(
        self,
        *,
        tmppath: Union[str, Path] = None,
        filter_outliers: bool = True,
        strategy: str = "random",
    ):
        super().__init__(tmppath=tmppath)
        self.filter_outliers = filter_outliers
        self._strategy = strategy
        self._holdout = Holdout()

    @property
    def SUPPORTED_DTYPES(self):  # noqa: N802
        return self._SUPPORTED_DTYPES

    def _select_pipeline_prototype(
        self, metadata: Metadata, data_types: Optional[dict] = None
    ) -> PipelinePrototype:
        preprocessor = SynthpopSegmentPreprocessor
        if metadata.shape[0] < 5_000 or metadata.shape[1] < 50 or metadata._is_multitable:
            preprocessor = IdentityPreprocessor
        pipeline_def = PipelinePrototype(
            dataset=PipelinePrototype.DatasetScope(
                preprocessor=SynthpopPreprocessor,
                preprocessor_params={"anonymize_config": self.anonymize,
                                     "metadata": metadata},
            ),
            segment=PipelinePrototype.SegmentScope(preprocessor=preprocessor,
                                                   preprocessor_params={
                                                       "metadata": metadata}
                                                   ),
            block=PipelinePrototype.BlockScope(
                synthesizer=RegularSynthesizerModel.SYNTHPOP.value
            ),
        )
        return pipeline_def

    @log_time_factory(logger)
    def fit(
        self,
        X: Dataset,
        metadata: Metadata,
        *,
        calculated_features: list[dict[str, str |
                                       Callable | List[str]]] | None = None,
        missing_values: list | None = None,
        anonymize: dict | AnonymizerConfigurationBuilder | None = None,
        privacy_level: PrivacyLevel | str = PrivacyLevel.HIGH_FIDELITY,
        condition_on: Union[str, list[str]] | None = None,
        anonymize_ids: bool = False,
        segment_by: SegmentByType = "auto",
        holdout_size: float = 0.2,
        random_state: RandomSeed = None
    ):
        self._check_invalid_values(metadata=metadata, holdout=holdout_size)
        self.anonymize = anonymize
        logger.debug(
            "[SYNTHESIZER] - Updating the metadata to only keep the columns to be synthesized.")

        # Transform into list in case user provides a string
        if condition_on is not None and isinstance(condition_on, str):
            condition_on = [condition_on]

        self._init_fit(metadata, segment_by, calculated_features,
                       anonymize, condition_on, anonymize_ids=anonymize_ids)

        # Create the train set based on a calculated holdout.
        if (holdout_size > 0.) and len(X) > 10000:
            logger.debug(
                f"[SYNTHESIZER] - Applying the holdout split with a {self._strategy} strategy.")
            train_X, _ = self._holdout.get_split(
                X=X, metadata=metadata, strategy=self._strategy, random_state=random_state
            )
            del X
        else:
            train_X = X

        # Select only the columns to be synthesized
        logger.debug(
            "[SYNTHESIZER] - Selecting only the columns to be synthesized.")
        cols = list(self.data_types.keys())
        train_X = train_X[cols]

        # update metadata
        # if len calculated_features>0
        metadata = metadata[cols]
        privacy_level = PrivacyLevel(privacy_level)

        # TODO: schema definition inference
        logger.debug("[SYNTHESIZER] - Starting the training procedure.")
        self._fit(train_X, metadata,
                  privacy_level=privacy_level,
                  condition_on=condition_on,
                  holdout_size=holdout_size,
                  random_state=random_state)
        self.is_fitted_ = True
        return self

    @log_time_factory(logger)
    @synthesizer_sample
    def sample(
        self,
        n_samples: int = 1,
        condition_on: list[ConditionalFeature] | dict | pdDataFrame | None = None,
        balancing: bool = False,
        random_state: RandomSeed = None,
        connector: BigQueryConnector | ObjectStorageConnector | RDBMSConnector | None = None,
        **kwargs
    ):

        result = super()._sample(n_samples, condition_on=condition_on,
                                 balancing=balancing, random_state=random_state)[:n_samples]

        output_schema = self._get_output_schema()

        for c in result.columns:
            if c in output_schema and output_schema[c] == "int":
                if result[c].dtypes in ["object", "category"]:
                    try:
                        result[c] = to_numeric(result[c].astype(float))
                    except ValueError:
                        result[c] = result[c].astype(str)
                        break  # No need to check for empty values
                if result[c].isna().values.any() > 0:
                    output_schema[c] = "float"
                else:
                    result[c] = to_numeric(result[c].astype(int))
            if self.is_multitable and output_schema[c] == "datetime":
                output_schema[c] = "int"

        output_schema, result = self._anonymizer_post_process(
            output_schema, result)

        output_schema, result = self._calculated_features_post_process(
            output_schema, result)

        result_dd = self._pandas_df_to_dask(result)
        dataset = Dataset(result_dd, schema=output_schema)

        logger.info(f'let write into the connector {connector}')
        logger.info(f'using kwargs {kwargs}')
        if connector:
            try:
                # test if we can connect to the connector
                connector.test()

                logger.info('write connector tested successfully')

                self._write_sample_to_connector(dataset, connector, **kwargs)

                logger.info('sample written into connector successfully')
            except Exception as e:
                logger.error(f'got error while writing to the connector {e}')

        return dataset

    @log_time_factory(logger)
    def _check_sample(self,
                      n_samples: int = 1,
                      post_transform: dict[str, Callable] = None,
                      post_filter: dict[str, Callable[[Any], bool]] = None) -> Dataset:
        self._m_get_n_segments_samples = partial(
            self._test_get_n_segments_samples, sample_per_block=n_samples)
        r = self.sample(n_samples, post_transform, post_filter)
        self._m_get_n_segments_samples = self._get_n_segments_samples
        return r
