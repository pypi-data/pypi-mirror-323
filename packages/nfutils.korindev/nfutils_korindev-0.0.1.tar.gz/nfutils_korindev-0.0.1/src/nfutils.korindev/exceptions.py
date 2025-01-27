class NFParseError(Exception):
    """Base exception for parsing errors."""
    pass

class InvalidFormatError(NFParseError):
    """Raised when the file format is invalid."""
    pass

class MissingFieldError(NFParseError):
    """Raised when a required field is missing."""
    pass