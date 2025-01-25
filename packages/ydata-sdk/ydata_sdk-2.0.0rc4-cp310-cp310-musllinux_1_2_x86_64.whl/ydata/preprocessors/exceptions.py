class MaxIteration(StopIteration):
    """Exception raised when a maximum number of iterations has been
    reached."""


class AnonymizerMaxIteration(Exception):
    """Exception raised by the synthesizer when a maximum number of iterations
    has been reached."""


class InvalidAnonymizer(Exception):
    """Exception raised when an Invalid Anonymizer is used."""


class InvalidAnonymizerConfig(Exception):
    """Exception raised when the configuration of a Anonymizer is invalid."""


class InvalidAnonymizerInputType(Exception):
    """Exception raised when the input type of the anonymizer is non
    categorical."""
