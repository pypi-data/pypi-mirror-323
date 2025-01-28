from logging import Logger
from typing import Type


def log_and_raise(
    name: str,
    message: str,
    exception_type: Type[Exception],
    logger: Logger = None,
    error: Exception = None,
) -> None:
    """
    Logs an error message and raises an exception.

    :param name: The name of the module or class that called.
    :param message: The error message.
    :param exception_type: The exception type to raise.
    :param logger: The logger to log the message.
    :param error: The error that caused the exception.
    :raises: exception_type:  {name}: {message}
    """

    if logger:
        logger.error(message, exc_info=True)

    raise exception_type(f"{name}: {message}") from error


__all__ = ["log_and_raise"]
