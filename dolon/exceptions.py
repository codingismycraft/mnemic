"""Dolon exceptions."""


class DolonException(Exception):
    """A generic Dolon exception."""


class InvalidMessage(DolonException):
    """Invalid message."""


class InvalidEnvironmentVariable(DolonException):
    """Invalid environment variable."""
