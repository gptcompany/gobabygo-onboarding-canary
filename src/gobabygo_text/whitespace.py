"""Whitespace normalization utilities for text processing."""

import re

__all__ = ["normalize_whitespace"]

_ASCII_WHITESPACE = " \t\n\r\v\f"
_ASCII_WHITESPACE_RUN = re.compile(r"[ \t\n\r\v\f]+")


def normalize_whitespace(value: str) -> str:
    """Normalize whitespace in a string by collapsing ASCII whitespace runs and stripping ends.

    Collapses every maximal run of one or more ASCII whitespace characters
    (space U+0020, horizontal tab U+0009, line feed U+000A, carriage return U+000D,
    vertical tab U+000B, form feed U+000C) to a single U+0020 space, and strips
    all leading and trailing ASCII whitespace.

    Non-ASCII whitespace characters (such as U+00A0 NO-BREAK SPACE and U+3000
    IDEOGRAPHIC SPACE) are ordinary content and are preserved verbatim.

    Args:
        value: The string to normalize. Must be an instance of str (or a subclass).

    Returns:
        A normalized string.

    Raises:
        TypeError: If value is not an instance of str. The error message includes
            the name of the received type.
    """
    if not isinstance(value, str):
        raise TypeError(
            f"normalize_whitespace() expected str, got {type(value).__name__}"
        )
    return _ASCII_WHITESPACE_RUN.sub(" ", value).strip(_ASCII_WHITESPACE)
