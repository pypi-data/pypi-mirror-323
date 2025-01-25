"""Option parser.

This module contains the logic to parse the options in the region.
"""

from typing import Final, Literal, cast

try:
    from typing import TypeAlias  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import TypeAlias


__all__ = (
    "option_parser",
    "Options",
    "make_string_from_options",
)


Options: TypeAlias = dict[str, str]

QUOTE_CHARS: Final = ("'", '"')
VALUE_QUOTED_TYPE: TypeAlias = Literal["'", '"', ""]


def option_parser(options_str: str) -> Options:  # noqa: C901
    """Parse the options of the region.

    :param options_str: The option string in format "key=value key2='value 2'"
    :return: Dictionary of parsed options
    :raise TypeError: If input is not a string
    :raise OptionParserError: If parsing fails

    Example:
        >>> option_parser('key="value" other=123')
        {'key': 'value', 'other': '123'}
    """
    if not isinstance(options_str, str):
        raise TypeError("options_str must be a string")

    options: dict[str, str] = {}
    option_name: str = ""
    option_value: str = ""

    is_value: bool = False

    # `""` means that the value is not quoted (example: `option=value`)
    value_quoted: VALUE_QUOTED_TYPE = ""

    def _reset_state() -> None:
        nonlocal option_name, option_value, is_value, value_quoted
        options[option_name.strip()] = option_value
        option_name = ""
        option_value = ""
        is_value = False
        value_quoted = ""

    for s in options_str.strip():
        if is_value:
            # We just started parsing the value
            if not option_value:
                # If the current character is a quote, then we're parsing a quoted value
                if s in QUOTE_CHARS:
                    value_quoted = cast(VALUE_QUOTED_TYPE, s)
                    continue

            # Found the closing quote and it the same as the opening quote
            if value_quoted and s == value_quoted:
                # If the previous character was a backslash, then we need to add this character to the value
                if option_value[-1] == "\\":
                    option_value = option_value[:-1] + s
                    continue

                # Otherwise, we're done parsing the value
                _reset_state()
                continue

            # Otherwise, we're parsing an unquoted value
            if not value_quoted and s == " ":
                _reset_state()
                continue

            option_value += s
            continue

        if s.startswith("="):
            is_value = True
            continue

        option_name += s

    if option_name and (option_value or value_quoted):
        _reset_state()

    return options


def make_string_from_options(options: Options) -> str:
    """Make a string from the options.

    :param options: The options.
    :return: The string.
    """
    return " ".join(f"{k.strip()}={v.strip()!r}" for k, v in options.items())
