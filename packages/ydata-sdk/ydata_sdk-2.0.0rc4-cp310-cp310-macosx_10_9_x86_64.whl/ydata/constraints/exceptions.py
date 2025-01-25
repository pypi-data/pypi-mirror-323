class ConstraintError(Exception):
    """Base class for all constraint exception."""

    pass


class NotValidatedError(ConstraintError):
    """Raised when a constraint or constraint engine was not validated."""

    pass


class ConstraintDoesNotExist(ConstraintError):
    """Raised when accessing a constraint which does not exist."""

    pass
