class TzSmmPayError(Exception):
    """Base class for all exceptions in the library."""
    pass

class AuthenticationError(TzSmmPayError):
    """Raised when authentication fails."""
    pass

class ValidationError(TzSmmPayError):
    """Raised when validation fails."""
    pass

class APIError(TzSmmPayError):
    """Raised when the API returns an error."""
    pass
