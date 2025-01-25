"""Utils exceptions module."""
from __future__ import absolute_import, division, print_function


class InvalidDatasetTypeError(ValueError):
    """Exception to be raised when and invalid DatasetType is provided."""


class InvalidPublishedDataset(KeyError):
    """Exception to be raised whenever a user is trying to get a non-published
    dataset."""


class ColumnNotFoundError(KeyError):
    """Exception to be raised whenever we try to access an invalid or non-
    existing column."""


class VariableTypeConversionError(TypeError):
    """Exception to be raised whenever we try to convert a variable type to an
    invalid variable type."""


class VariableTypeRequestError(TypeError):
    """Exception to be raised whenever the request to convert multiple variable
    types is not correct."""


class DataTypeRequestError(TypeError):
    """Exception to be raised whenever the request for datatype is
    incorrect."""


class InvalidEntityColumnError(TypeError):
    """Exception to be raised whenever the entity column is invalid."""


class NotEnoughRows(Exception):
    """Exception raised when the training dataset has too few rows."""


class LessRowsThanColumns(Warning):
    """Warning to be raised when the training dataset has less rows than
    columns."""


class SmallTrainingDataset(Warning):
    """Warning to be raised when the training dataset is small."""


class IgnoredParameter(Warning):
    """Warning to be raised when a parameter is not used."""
