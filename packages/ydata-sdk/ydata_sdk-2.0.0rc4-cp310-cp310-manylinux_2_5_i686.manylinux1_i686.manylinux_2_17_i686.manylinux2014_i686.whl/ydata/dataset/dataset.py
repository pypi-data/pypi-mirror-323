"""Dataset definition file."""
from __future__ import annotations

import warnings
from typing import Dict, List, Literal, Optional, Tuple, Union
from warnings import warn

import dask
import dask.dataframe as dd
from dask.dataframe import DataFrame as ddDataframe
from dask.dataframe import Series as ddSeries
from dask.dataframe.core import Scalar as ddScalar
from dask.delayed import Delayed
from numpy import ndarray
from pandas import DataFrame as pdDataframe
from pandas import Series as pdSeries

from ydata.dataset.engines import VALID_ENGINES, to_dask, to_numpy, to_pandas
from ydata.dataset.schemas import DatasetSchema as Schema
from ydata.dataset.utils import humanize_dtypes
from ydata.utils.configuration import TextStyle
from ydata.utils.data_types import VariableType
from ydata.utils.exceptions import VariableTypeRequestError
from ydata.utils.type_inference import DEFAULT_TYPES, TypeConverter, default_inference


class Dataset:
    """Dataset class provides the interface to handle data within YData's
    platform.

    Arguments:
        df (Union[pd.DataFrame, dd.DataFrame]): Dataset
        schema (Optional[Dict]): Mapping of column names to datatypes
        sample (float): Fraction of the sampled dataset
        index (str): Name of the column to be used as index
        missing_values (list or value): list of markers for missing values

    Properties:
        columns (list[str]): list of column names
        nrows (tuple): number of rows from the training and test datasets
        ncols (int): number of columns
        shape (tuple): tuple of (nrows, ncols)
        memory_usage (int): number of bytes consumed by the underlying dataframe
        nmissings (int): total number of missings in Dataset
        infered_dtypes_count (Dict[str, Dict]): infered data types per column
        infered_dtypes (Dict[str, str]): infered data type per column
        dtypes (Dict[str, str]): mapping of data type per column, either provided or inferred
        index (str): Returns the name of the index column

    Methods:
        enforce_dtypes: enforces a schema of data types, defaults to inferred
        select_dtypes: subset Dataset column based on features' data types
        to_pandas, to_numpy, to_dask: returns a Dataset as a pandas dataframe, numpy array or dask dataframe
        value_counts: number of value occurrences for given column
        uniques: number of unique values for given column
        drop_columns: drops specific columns from a Dataset
        select_columns: select specific columns from a Dataset
        reorder_columns: defines the order of columns for underlying data
        sample: returns a sample from the original Dataset

    Magic Methods:
        __len__: equal to nrows
        __contains__: checks whether a column is in a Dataset
        __getitem__: equal to select_columns
    """

    def __init__(
        self,
        df: VALID_ENGINES,
        schema: dict[str, Schema] | None = None,
        sample: float = 0.2,
        index: str | dask.dataframe.core.Index | None = None,
        divisions: list | tuple | None = None,
    ):
        # Setting dataset, dataset type and index
        data = to_dask(df)
        self._index = index

        if all([val in ["object", "string"] for col, val in data.dtypes.items()]):
            warnings.warn(
                "All the input Variable Types were set as `string` or `object`. "
                "It is recommend to revise the VariableType settings for optimal results."
            )
        # This is the time-consuming step
        data = self.__set_index(
            data=data, index=self._index, divisions=divisions)
        if schema:
            try:
                # sanitize parameter
                self._schema = {
                    c: v if isinstance(v, Schema) else Schema(
                        column=c, vartype=VariableType(v))
                    for c, v in schema.items()
                }

                _schema = {
                    c: VariableType(v.vartype).value for c, v in self._schema.items()
                }

                assert all(
                    [col in data.columns for col in schema.keys()]
                ), "Not all the dataset columns are defined in the schema. Please validate your input."
                assert all(
                    [dtype in DEFAULT_TYPES for dtype in set(_schema.values())]
                ), f"Not all dtypes provided ({_schema}) are supported. Valid dtypes => ({DEFAULT_TYPES})"
                data = data[list(_schema.keys())]

                # THIS CONVERSIONS WILL BE DONE LATER BY astype FUNCTION
                # for k, v in _schema.items():
                #     if v in ["date", "time", "datetime"]:
                #         _schema[k] = "datetime64[ns]"
                # MOVED TO THE SAMPLE METHOD TO AVOID INVOKING COMPUTE.
                # elif v == "int" and df[k].isna().values.any() > 0:
                #     # Pandas/Dask cannot convert to int if missing value
                #     # See: https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html
                #     schema[k] = "float"
                #     warnings.warn(
                #         "The column {} has missing data. "
                #         "Int is not a supported VariableType for columns with missing data."
                #     )

                date_cols = {}
                for k, v in _schema.copy().items():
                    col_info = self._schema[k]
                    if v in ['date', 'time', 'datetime'] and col_info.format is not None:
                        date_cols[k] = col_info
                        _schema.pop(k)
                    elif v in ['date', 'time', 'datetime'] and col_info.format is None:
                        date_cols[k] = col_info
                        _schema[k] = "datetime64[ns]"

                if len(date_cols.keys()) > 0:
                    for col, v in date_cols.items():
                        if v.format:
                            data[col] = dd.to_datetime(
                                data[col], format=v.format, errors="coerce")
                        else:
                            data[col] = dd.to_datetime(
                                data[col], errors="coerce")

            except ValueError as e:
                raise Exception(f"Please provide a valid schema - {e}")
        else:
            dtypes, _schema = humanize_dtypes(data.dtypes.to_dict())
            self._schema = {col: Schema(column=col, vartype=VariableType(v))
                            for col, v in dtypes.items()}

        self._data = data.astype(_schema)
        self._nrows = None
        self._dtypes_count = None
        self._missings = None
        self._n_uniques = {}
        self.__sample = sample

    def __set_sample(self, sample):
        self.__sample = sample
        return

    def copy(self) -> Dataset:
        """Copy a Dataset instance.

        Returns:
            dataset (Dataset): A new Dataset instance with the scame schema and index.
        """
        return Dataset(self._data, schema=self._schema, index=self.index)

    @staticmethod
    def __create_dask_dataframe_index(data: ddDataframe) -> ddDataframe:
        data = data.assign(idx=1)
        data.index = data["idx"].cumsum() - 1
        data = data.drop(columns=["idx"])
        data = data.set_index(data.index, sorted=True)
        data.divisions = data.compute_current_divisions()
        return data

    @staticmethod
    def __set_index(
        data: ddDataframe,
        index: str | dask.dataframe.core.Index | None = None,
        divisions: list | tuple | None = None,
    ) -> ddDataframe:
        """Asserts existence of the index column and sets it as new index."""
        if index is not None or data.index is not None:
            if isinstance(index, dask.dataframe.core.Index):
                data.index = index
            elif index:
                assert (
                    index in data.columns
                ), f"Provided index {index} does not exist in the dataframe columns."

            if divisions:
                data = data.repartition(divisions=divisions)
        else:
            data = Dataset.__create_dask_dataframe_index(data)

        return data

    @property
    def ncols(self) -> int:
        "Return the number of columns"
        return len(self.columns)

    @property
    def nrows(self) -> int:
        "Return the number of rows"
        if self._nrows is None:
            self._nrows = len(self._data)
        return self._nrows

    @property
    def columns(self) -> list[str | int]:
        "Return dataset columns."
        return list(self._data.columns)

    @property
    def index(self) -> Optional[str]:
        "Returns the name of the index column"
        return self._index

    @property
    def loc(self):
        """Label location based indexer for selection. This method is inherited
        from Dask original LocIndexer implementation.

        >>> df.loc["b"]
        >>> df.loc["b":"d"]
        """
        from dask.dataframe.indexing import _LocIndexer

        return _LocIndexer(self._data)

    @property
    def schema(self) -> dict:
        return {val.column: VariableType(val.vartype) for val in self._schema.values()}

    @schema.setter
    def schema(self, new_value: dict[str, VariableType | str]):
        for col, val in new_value:
            old_schema = self._schema[col]
            self._schema[col] = Schema(
                column=col, vartype=VariableType(val), format=old_schema.format)

    def apply(
        self,
        function: callable,
        axis: Union[int, str] = 1,
        raw: bool = False,
        args: Optional[Tuple] = None,
        meta: Optional[Union[Dict, List[Tuple],
                             Tuple, Dataset]] | str = "__no_default__",
    ) -> Dataset:
        """Parallelized version of apply.

        Only supported on the rows axis.
        To guarantee results with expected format, output metadata should be provided with meta argument.
        Arguments:
            function (callable): Function to apply to each row
            axis (Union[int, str]): 1/'columns' apply function to each row.
                0/'index' apply function to each column is not supported.
            raw (bool): Passed function operates on Pandas Series objects (False), or numpy arrays (True)
            args (Optional[Tuple]): Positional arguments to pass to function in addition to the array/series
            meta (Optional[Union[Dict, List[Tuple], Tuple, Dataset]]): A dictionary, list of tuples, tuple or dataset
                that matches the dtypes and column names of the output. This is an optional argument since it only
                certifies that Dask will use the correct metadata instead of infering which may lead to unexpected
                results.
        Returns:
            df (Dataset): A dataset object output of function.
        """
        if axis not in [1, "columns"]:
            raise NotImplementedError(
                f"The axis argument {axis} is not supported. Please use 1 or columns."
            )
        if isinstance(meta, Dataset):
            meta = meta._data
        if not args:
            args = ()
        data = self._data.apply(function, axis=axis,
                                raw=raw, args=args, meta=meta)
        if isinstance(data, ddSeries):
            data = data.to_frame(name=data.name)
        return Dataset(data, index=self.index, divisions=self._data.divisions)

    def shape(
        self, lazy_eval=True, delayed=False
    ) -> tuple[int | Delayed | None, int]:
        """Returns dataset shape as a tuple (rows, columns).

        Supports lazy evaluation of nrows, ncols is unexpensive and
        returned directly
        """
        if lazy_eval:
            return (self._nrows, self.ncols)
        else:
            if delayed:
                return (self.nrows, self.ncols)
            else:
                return (dask.compute(self.nrows)[0], self.ncols)

    @property
    def memory_usage(self) -> ddSeries:
        "Calculates the memory usage of the Dataset."
        return self._data.memory_usage()

    def missings(self, compute=False) -> Union[ddSeries, pdSeries]:
        """Calculates the number of missing values in a Dataset.

        #TODO: Define missing as not-parsed from string_parser
                instead of native Dask computation.
        """
        if self._missings is None:
            self._missings = self._data.isnull().sum()
        if compute and isinstance(self._missings, ddSeries):
            self._missings = self._missings.compute()
        return self._missings

    @property
    def nmissings(self) -> int:
        "Returns the total count of missings in a Dataset"
        missings = self.missings(compute=True)
        return int(sum(missings.values))

    @property
    def __infered_dtypes_count(self) -> dict:
        """Calculates the infered value types per column."""
        if self._dtypes_count is None:
            infered_dtypes = self._data.sample(frac=self.__sample).applymap(
                default_inference.infer
            )
            calc_dtypes = dd.compute(
                [infered_dtypes[col].value_counts()
                 for col in infered_dtypes.columns]
            )[0]
            self._dtypes_count = {col.name: col.to_dict()
                                  for col in calc_dtypes}
        return self._dtypes_count

    def infer_dtypes(self, schema: Optional[dict] = None):
        """Infers the schema based on the dtypes count.

        A feature is assigned to a dtype if its values represent the
        majority of its values.
        """
        # TODO : Infer only for columns with missing initialization
        if schema is None:
            schema = {}
            for (
                feat,
                counts,
            ) in self.__infered_dtypes_count.items():  # for each feature
                keys = list(counts.keys())
                if (
                    "bool" in counts and "int" in counts
                ):  # if themisinge are ints, all bool_ints should also be ints
                    counts["int"] += counts["bool"]
                    counts["bool"] = 0
                if (
                    "float" in counts and "int" in counts
                ):  # if there are floats, all ints should also be floats
                    counts["float"] += counts["int"]
                    counts["int"] = 0
                if "date" in counts and len(keys) > 1:
                    total_counts = sum(counts.values())
                    counts = dict.fromkeys(counts, 0)
                    counts["date"] = total_counts

                schema[feat] = max(counts, key=counts.get)

        # assign feature dtype if representativity is highest
        dtype_implementation = {k: TypeConverter.to_low(
            v) for (k, v) in schema.items()}
        self._data = self._data.astype(dtype_implementation)

        self._schema = {col: Schema(column=col, vartype=VariableType(v))
                        for col, v in schema.items()}

    def select_dtypes(
        self,
        include: str | list | None = None,
        exclude: str | list | None = None,
    ) -> Dataset:
        """Returns a subset of the original Dataset based on the data types."""
        if include is None and exclude is None:
            raise ValueError(
                "Either 'include' or 'exclude' arguments must be provided."
            )
        elif include:
            return self.select_columns(self._select_dtypes_vars(include))
        elif exclude:
            return self.drop_columns(self._select_dtypes_vars(exclude))
        else:
            raise Exception(
                f"Could not determine how to select data types based on include ({include}) and exclude ({exclude}) arguments."
            )

    def _select_dtypes_vars(self, dtypes: Union[str, VariableType, list]) -> list:
        "Returns a list of variables based on their data type."
        # Accept either singular or list of values.
        _dtypes = dtypes if isinstance(dtypes, list) else [dtypes]
        _dtypes = [
            VariableType(dtype) if isinstance(dtype, str) else dtype
            for dtype in _dtypes
        ]
        return [k for (k, v) in self._schema.items() if VariableType(v.vartype) in _dtypes]

    def astype(self, column: str, vartype: Union[VariableType, str], format: Optional[str] = None):
        self._data = _astype(self._data, column, vartype=VariableType(
            vartype).value, format=format)

        self._schema[column] = Schema(
            column=column,
            vartype=VariableType(
                TypeConverter.from_low(self._data[column].dtype))
            if VariableType(vartype) != VariableType.DATE else VariableType.DATE
        )

    def update_types(self, dtypes: list):
        invalid_dtypes = [e for e in dtypes if any(
            m not in e for m in ['column', 'vartype'])]
        if len(invalid_dtypes):
            raise VariableTypeRequestError('Invalid dtype update request:\n {}\n All items must specify a `column` and `vartype`'.format(
                ', \n '.join(map(str, invalid_dtypes))))

        invalid_dtypes = [e['column']
                          for e in dtypes if e['column'] not in self._schema.keys()]
        if len(invalid_dtypes):
            raise VariableTypeRequestError(
                'Invalid dtype update request. The following columns do not exist: {}'.format(', '.join(invalid_dtypes)))

        for e in dtypes:
            self.astype(**e)

    def to_pandas(self) -> pdDataframe:
        "Returns a Dataset as a Pandas DataFrame."
        df = to_pandas(self._data)
        return df

    def to_numpy(self) -> ndarray:
        "Returns a Dataset as a Numpy Array."
        df = to_numpy(self._data)
        return df

    def to_dask(self) -> ddDataframe:
        "Returns a Dataset as a Dask Dataframe."
        return to_dask(self._data)

    def value_counts(self, col: str, compute=True) -> Union[ddSeries, pdSeries]:
        "Calculates the exact number of value occurrences for a given column."
        value_counts = self._data[col].value_counts()
        if compute:
            return value_counts.compute()
        return value_counts

    def uniques(self, col: str, approx=True, delayed=False) -> Union[int, ddScalar]:
        "Calculates the (exact/approximate) number of unique values in a column."
        # TODO: Enable parallel .compute() if called on multiple columns.

        # Priorities:
        # 0. only store value if exact. override approx if exact is available.
        # 1. return if already calculated
        # 2. leverage _n_uniques pre-computation if available.
        # 3. if approximate, return and skip storage

        if col not in self._n_uniques:
            if approx:
                n_uniques = self._data[col].nunique_approx()
            else:
                n_uniques = self._data[col].nunique()

            if not delayed:
                n_uniques = int(n_uniques.compute())
                self._n_uniques[col] = n_uniques

        else:
            n_uniques = self._n_uniques[col]
        return n_uniques

    def _filter_dropped_columns_values(self, columns: Union[str, list]):
        columns = columns if isinstance(columns, list) else [columns]
        self._filter_uniques(columns)
        self._filter_schema(columns)
        self._filter_missings(columns)
        self._filter_dtypes_count(columns)

    def _filter_uniques(self, columns: list):
        """Filter columns from uniques."""
        self._n_uniques = {
            k: v
            for k, v in self._n_uniques.items()
            if k not in columns
        }

    def _filter_schema(self, columns: list):
        """Filter columns from schema."""
        self._schema = {k: v for k, v in self._schema.items()
                        if k not in columns}

    def _filter_missings(self, columns: list):
        """Filter columns from missings."""
        if self._missings is None:
            return
        elif isinstance(self._missings, ddSeries):
            self._missings = None
        else:
            columns = columns if isinstance(columns, list) else [columns]
            filtered = [col for col in self.columns if col not in columns]
            self._missings = self._missings.loc[filtered]

    def _filter_dtypes_count(self, columns: list):
        """Fileter columns from _dtypes_count."""
        if self._dtypes_count is None:
            return
        self._dtypes_count = {
            k: v
            for k, v in self._dtypes_count.items()
            if k not in columns
        }

    def drop_columns(
        self, columns: Union[str, list], inplace=False
    ) -> Optional[Dataset]:
        """Drops specified columns from a Dataset.

        Args:
            columns (str or list): column labels to drop
            inplace (bool): if False, return a copy. Otherwise, drop inplace and return None.
        """
        # Validate wether the columns exist
        if inplace:
            self._data = self._data.drop(columns=columns)
            self._filter_dropped_columns_values(columns)
        else:
            return Dataset(self._data.drop(columns=columns))

    def select_columns(self, columns: Union[str, list], copy=True) -> Dataset:
        """Returns a Dataset containing only the subset of specified columns.
        If columns is a single feature, returns a Dataset with a single column.

        Args:
            columns (str or list): column labels to select
            copy (bool): if True, return a copy. Otherwise, select inplace and return self.
        """
        columns = columns if isinstance(columns, list) else [columns]
        data = self._data[columns]

        if copy:
            schema = {k: v for k, v in self._schema.items()
                      if k in columns}
            return Dataset(data, schema=schema)
        else:
            dropped_cols = [col for col in self.columns if col not in columns]
            self._data = data
            self._filter_dropped_columns_values(dropped_cols)
            return self

    def query(self, query: str) -> Dataset:
        return Dataset(self._data.query(query).copy())

    def _sample_fraction(self, sample: int) -> float:
        """Sample either deterministic number of rows (exact, slow) or
        percentage of total (approximate, fast).

        Dask Dataframes API requires fraction sampling, so we convert into percentage of total if exact number of rows are requested.

        Usage:
            >>> data._sample_fraction(sample=0.01)
            0.01
            >>> data.nrows, data._sample_fraction(sample=10)
            20, 0.5

        Args:
            sample (Union[float, int]): exact number of rows or percentage of total
            nrows (int, optional): number of rows if already calculated.

        Returns:
            calc_sample (float): applicable percentage to sample from dataset.
        """
        rows = self.nrows
        if sample >= rows:
            # size is either provided (total_rows) or calculated (nrows(df))
            return 1
        elif 1 < sample < rows:  # if pct of total
            return sample / self.nrows
        else:
            raise Exception(f"Requested sample ({sample}) is not valid.")

    def sample(
        self,
        size: Union[float, int],
        strategy: Literal["random", "stratified"] = "random",
        **strategy_params,
    ) -> Dataset:
        "Returns a sample from the original Dataset"
        from ydata.utils.sampling.random import RandomSplitSampler
        from ydata.utils.sampling.stratified import StratifiedSampler

        strategies = {"random": RandomSplitSampler,
                      "stratified": StratifiedSampler}

        if isinstance(size, float):
            assert 0 < size < 1, f"Requested sample size ({size}) is not valid."
            frac = size
        else:
            frac = self._sample_fraction(size)

        sampler = strategies[strategy](**strategy_params)
        return sampler.sample(self, frac=frac)

    def reorder_columns(self, columns: List[str]) -> Dataset:
        """Defines the order of the underlying data based on provided 'columns'
        list of column names.

        Usage:
            >>> data.columns
            ['colA', 'colB', colC']
            >>> data.reorder_columns(['colB', 'colC']).columns
            ['colB', 'colC']
        """
        return Dataset(self._data.loc[:, columns])

    def divisions(self) -> tuple:
        return self._data.divisions

    def sort_values(self, by: List[str], ignore_index: bool = True, inplace: bool = False) -> Optional[Dataset]:
        data = self._data.sort_values(by=by, ignore_index=ignore_index)
        if inplace:
            self._data = data
        else:
            return Dataset(data)

    def sorted_index(self, by: List[str]) -> pdSeries:
        return self._data[by] \
            .repartition(npartitions=1).reset_index(drop=True) \
            .sort_values(by=by).compute() \
            .index.to_frame(index=False).iloc[:, 0]

    @property
    def known_divisions(self) -> bool:
        return self._data.known_divisions

    def head(self, n=5) -> pdDataframe:
        """Return the `n` first rows of a dataset.

        If the number of rows in the first partition is lower than `n`,
        Dask will not return the requested number of rows (see
        `dask.dataframe.core.head` and `dask.dataframe.core.safe_head`).
        To avoid this corner case, we retry using all partitions -1.
        """
        head_df = self._data.head(n, npartitions=1, compute=True)
        if head_df.shape[0] < n:
            head_df = self._data.head(n, npartitions=-1, compute=True)
        return head_df

    def tail(self, n=5) -> pdDataframe:
        return self._data.tail(n, compute=True)

    ##################
    # Dunder methods #
    ##################
    def __len__(self) -> int:
        """Implements utility to call len(Dataset) directly, returning the
        number of rows.

        Usage:
        >>> len(data)
        """
        return self.nrows

    def __contains__(self, key) -> bool:
        """True if key is in Dataset columns.

        Usage:
        >>> 'my_column' in data
        """
        return key in self.columns

    def __getitem__(self, key) -> Dataset:
        """
        Usage:
        >>> data[ ['columnA', 'columnB'] ]
        """
        return self.select_columns(key)

    def _build_repr(self) -> dict:
        dataset = {
            "Shape": self.shape(lazy_eval=False, delayed=False),
            "Schema": pdDataframe(
                [
                    {"Column": k, "Variable type": v.vartype.value}
                    for k, v in self._schema.items()
                ]
            ),
        }
        return dataset

    def __str__(self) -> str:
        """Dunder method to pretty print the content of the object Dataset."""
        pretty_summary = self._build_repr()
        str_repr = TextStyle.BOLD + "Dataset \n \n" + TextStyle.END
        for k, val in pretty_summary.items():
            str_repr += TextStyle.BOLD + f"{k}: " + TextStyle.END
            if type(val) != pdDataframe:
                str_repr += str(val)
            else:
                str_repr += "\n"
                str_repr += val.to_string() + "\n"
            str_repr += "\n"
        return str_repr


def _astype(data: ddDataframe, column: str, vartype: str, format: str | None = None) -> ddDataframe:
    if vartype in ["date", "time", "datetime"]:
        data[column] = dd.to_datetime(
            data[column], format=format, errors="coerce").dt.tz_localize(None)
    else:
        data = data.astype({column: vartype})

        if format is not None:
            warn("Parameter 'format' is valid only for vartype='datetime'")

    return data
