from typing import Any

import pytest

from text_region_parser.options import make_string_from_options, option_parser


@pytest.mark.basic
@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        pytest.param(
            "key=value",
            {"key": "value"},
            id="simple_key_value",
        ),
        pytest.param(
            "key1=value1 key2=value2",
            {"key1": "value1", "key2": "value2"},
            id="multiple_key_value_pairs",
        ),
        pytest.param(
            'name="John Doe" age="30"',
            {"name": "John Doe", "age": "30"},
            id="quoted_values",
        ),
        pytest.param(
            "single='value' double=\"value\"",
            {"single": "value", "double": "value"},
            id="mixed_quotes",
        ),
        pytest.param(
            'description="This is a long description" title="My Title"',
            {"description": "This is a long description", "title": "My Title"},
            id="spaces_in_values",
        ),
        pytest.param(
            r'message="Hello \"World\""',
            {"message": 'Hello "World"'},
            id="escaped_quotes",
        ),
        pytest.param(
            'key=""',
            {"key": ""},
            id="empty_value",
        ),
        pytest.param(
            "key1=value1    key2=value2",
            {"key1": "value1", "key2": "value2"},
            id="multiple_spaces",
        ),
    ],
)
def test_normal_input(input_string: str, expected: dict[str, str]):
    """Test various option parsing scenarios"""
    result = option_parser(input_string)
    assert result == expected


@pytest.mark.basic
@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        pytest.param(
            "",
            {},
            id="empty_string",
        ),
        pytest.param(
            'key="unclosed',
            {"key": "unclosed"},
            id="unclosed_quotes",
        ),
        pytest.param(
            "key =value",
            {"key": "value"},
            id="space_before_equals",
        ),
        pytest.param(
            "key= value",
            {"key": ""},
            id="space_after_equals",
        ),
        pytest.param(
            "key=",
            {},
            id="missing_value",
        ),
        pytest.param(
            "=value",
            {},
            id="missing_key",
        ),
        pytest.param(
            "key value",
            {},
            id="missing_equals_sign",
        ),
        pytest.param(
            "key",
            {},
            id="missing_equal_signs",
        ),
        pytest.param(
            "=",
            {},
            id="single_equals_sign",
        ),
    ],
)
def test_malformed_input(input_str: str, expected: dict[str, str]):
    """Test handling of malformed input"""
    assert option_parser(input_str) == expected


@pytest.mark.basic
@pytest.mark.parametrize(
    ("input_string", "expected"),
    [
        pytest.param('key="值" emoji="🚀"', {"key": "值", "emoji": "🚀"}, id="unicode_values"),
        pytest.param('漢字="value"', {"漢字": "value"}, id="unicode_keys"),
    ],
)
def test_unicode_handling(input_string: str, expected: dict[str, str]) -> None:
    assert option_parser(input_string) == expected


@pytest.mark.basic
@pytest.mark.parametrize(
    ("options", "expected"),
    [
        pytest.param(
            {"key": "value"},
            'key="value"',
            id="simple_key_value",
        ),
        pytest.param(
            {"k1": "v1", "k2": "v2"},
            'k1="v1" k2="v2"',
            id="multiple_pairs",
        ),
    ],
)
def test_make_string_from_options(options: dict[str, str], expected: str) -> None:
    """Test conversion of options dictionary to string.

    :param options: Input options dictionary.
    :param expected: Expected string output.
    """
    result = make_string_from_options(options)
    parsed_result = option_parser(result)
    assert parsed_result == options


@pytest.mark.basic
@pytest.mark.parametrize(
    "invalid_input",
    [
        pytest.param(None, id="none_input"),
        pytest.param(123, id="integer_input"),
        pytest.param([], id="list_input"),
        pytest.param({}, id="dict_input"),
    ],
)
def test_invalid_input_types(invalid_input: Any) -> None:
    """Test handling of invalid input types.

    :param invalid_input: Various invalid input types.
    """
    with pytest.raises(TypeError):
        option_parser(invalid_input)  # type: ignore


@pytest.mark.doctest
def test_docstring_examples() -> None:
    """Test that docstring examples work as documented."""
    import doctest

    import text_region_parser.options as options_module

    results = doctest.testmod(options_module)
    assert results.failed == 0
