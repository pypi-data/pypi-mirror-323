import logging
from typing import Any, TypedDict, cast

import pytest

from text_region_parser.region_constructor import InvalidOptionsError, RegionConstructor

CONTENT = "\ncontent\n"
REGION_NAME = "test"


class OptionsForTest(TypedDict):
    key: str
    value: str


def create_test_parser(options: OptionsForTest) -> str:
    """Create test content from options.

    :param options: Parser options.
    :return: Generated content.
    """
    return f"key={options['key']}, value={options['value']}"


def create_region_content(
    region_name: str = REGION_NAME,
    content: str = CONTENT,
    options: str = "",
) -> str:
    """Helper function to create region content strings.

    :param region_name: Name of the region.
    :param content: Content of the region.
    :param options: Options string for the region.
    :return: Complete region string.
    """
    options_str = f" {options}" if options else ""
    return f"<!-- region:{region_name}{options_str} -->{content}<!-- endregion:{region_name} -->"


@pytest.mark.basic
def test_constructor_basic() -> None:
    """Test basic constructor functionality."""
    constructor = RegionConstructor()
    assert isinstance(constructor._parsers, dict)
    assert len(constructor._parsers) == 0


@pytest.mark.basic
def test_add_parser() -> None:
    """Test parser registration."""
    constructor = RegionConstructor()

    @constructor.add_parser("test", options_type=OptionsForTest)
    def test_parser(options: OptionsForTest) -> str:
        return create_test_parser(options)

    assert "test" in constructor._parsers
    assert callable(constructor._parsers["test"])


@pytest.mark.basic
@pytest.mark.parametrize(
    ("region_name", "options_type", "error_type", "error_message"),
    [
        pytest.param(
            123,
            None,
            TypeError,
            "Region name must be a string",
            id="invalid_region_name_type",
        ),
        pytest.param(
            "test space",
            None,
            ValueError,
            "Invalid region name format",
            id="invalid_region_name_format",
        ),
        pytest.param(
            "test",
            dict,
            TypeError,
            "options_type must be a TypedDict subclass",
            id="invalid_options_type",
        ),
    ],
)
def test_add_parser_validation(
    region_name: Any,
    options_type: Any,
    error_type: type[Exception],
    error_message: str,
) -> None:
    """Test parser registration validation.

    :param region_name: Name of the region to register.
    :param options_type: Type for options validation.
    :param error_type: Expected error type.
    :param error_message: Expected error message.
    """
    constructor = RegionConstructor()

    with pytest.raises(error_type, match=error_message):
        constructor.add_parser(region_name, options_type)(create_test_parser)  # type: ignore


@pytest.mark.basic
def test_parse_content_basic() -> None:
    """Test basic content parsing."""
    constructor = RegionConstructor()

    @constructor.add_parser("test", options_type=OptionsForTest)
    def test_parser(options: OptionsForTest) -> str:
        return create_test_parser(options)

    content = create_region_content("test", CONTENT, "key='test' value='value'")
    result = constructor.parse_content(content)

    assert "key=test, value=value" in result


@pytest.mark.basic
@pytest.mark.parametrize(
    ("content", "error_type", "error_message"),
    [
        pytest.param(
            None,
            TypeError,
            "content must be a string",
            id="none_content",
        ),
        pytest.param(
            123,
            TypeError,
            "content must be a string",
            id="non_string_content",
        ),
    ],
)
def test_parse_content_validation(content: Any, error_type: type[Exception], error_message: str) -> None:
    """Test content parsing validation.

    :param content: Content to parse.
    :param error_type: Expected error type.
    :param error_message: Expected error message.
    """
    constructor = RegionConstructor()
    with pytest.raises(error_type, match=error_message):
        constructor.parse_content(content)  # type: ignore


@pytest.mark.error_handling
def test_parser_invalid_options(caplog: pytest.LogCaptureFixture) -> None:
    """Test handling of invalid options in parser."""
    constructor = RegionConstructor()

    @constructor.add_parser("test", options_type=OptionsForTest)
    def test_parser(options: OptionsForTest) -> str:
        raise InvalidOptionsError("Invalid options")

    content = create_region_content("test", CONTENT, "key='test' value='value'")

    with caplog.at_level(logging.ERROR):
        result = constructor.parse_content(content)
        assert "Invalid options for region test: Invalid options" in caplog.text
        assert result == content


@pytest.mark.error_handling
def test_parser_invalid_return_type(caplog: pytest.LogCaptureFixture) -> None:
    """Test handling of invalid return type from parser."""
    constructor = RegionConstructor()

    @constructor.add_parser("test", options_type=OptionsForTest)
    def test_parser(options: OptionsForTest) -> str:
        return cast(str, 123)  # type: ignore

    content = create_region_content("test", CONTENT, "key='test' value='value'")

    with caplog.at_level(logging.ERROR):
        result = constructor.parse_content(content)
        assert "Parser for region test returned int instead of str" in caplog.text
        assert result == content


@pytest.mark.formatting
def test_multiple_regions() -> None:
    """Test handling of multiple regions."""
    constructor = RegionConstructor()

    @constructor.add_parser("test", options_type=OptionsForTest)
    def test_parser(options: OptionsForTest) -> str:
        return create_test_parser(options)

    content = (
        create_region_content("test", CONTENT, 'key="test1" value="value1"')
        + "\n"
        + create_region_content("test", CONTENT, 'key="test2" value="value2"')
    )
    result = constructor.parse_content(content)

    assert "key=test1, value=value1" in result
    assert "key=test2, value=value2" in result


@pytest.mark.formatting
def test_nested_regions() -> None:
    """Test handling of nested regions."""
    constructor = RegionConstructor()

    @constructor.add_parser("outer", options_type=OptionsForTest)
    def outer_parser(options: OptionsForTest) -> str:
        return f"outer: {create_test_parser(options)}"

    @constructor.add_parser("inner", options_type=OptionsForTest)
    def inner_parser(options: OptionsForTest) -> str:
        return f"inner: {create_test_parser(options)}"

    inner_content = create_region_content("inner", CONTENT, "key='inner' value='value'")
    content = create_region_content("outer", inner_content, "key='outer' value='value'")

    result = constructor.parse_content(content)
    assert "outer: key=outer, value=value" in result
    assert "inner: key=inner, value=value" not in result


@pytest.mark.doctest
def test_docstring_examples() -> None:
    """Test that docstring examples work as documented."""
    import doctest

    import text_region_parser.region_constructor as constructor_module

    results = doctest.testmod(constructor_module)
    assert results.failed == 0
