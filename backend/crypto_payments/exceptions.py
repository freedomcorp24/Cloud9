"""Exceptions for cryptocurrency payment processing."""

class NodeError(Exception):
    """Base exception for node-related errors."""
    pass

class NodeConnectionError(NodeError):
    """Exception raised when connection to node fails."""
    pass

class NodeAuthenticationError(NodeError):
    """Exception raised when node authentication fails."""
    pass

class NodeTimeoutError(NodeError):
    """Exception raised when node request times out."""
    pass

class NodeResponseError(NodeError):
    """Exception raised when node returns invalid response."""
    pass

class InsufficientFundsError(NodeError):
    """Exception raised when wallet has insufficient funds."""
    pass

class InvalidAddressError(NodeError):
    """Exception raised when cryptocurrency address is invalid."""
    pass

class TransactionError(NodeError):
    """Exception raised when transaction creation/broadcast fails."""
    pass
