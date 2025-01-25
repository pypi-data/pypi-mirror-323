import os
import threading
import time
from typing import Any, Union

import psutil
import pytest

from text_region_parser.region_class import Region, RegionExtended
from text_region_parser.region_parser import get_region

CONTENT = "\ncontent\n"
REGION_NAME = "test"
LARGE_CONTENT_SIZE = 50_000_000  # 50 MB
LARGE_CONTENT_TIMEOUT = 0.1  # 100 milliseconds


def create_region_content(
    region_name: str = REGION_NAME, content: str = "", with_options: Union[bool, str] = False
) -> str:
    """Helper function to create region content strings."""
    options = ""
    if with_options:
        if isinstance(with_options, bool):
            options = " key='value'"
        else:
            options = " " + with_options
    return f"<!-- region:{region_name}{options} -->{content}<!-- endregion:{region_name} -->"


@pytest.mark.basic
def test_region_basic() -> None:
    region = Region(name=REGION_NAME)
    assert region.name == REGION_NAME
    assert region.content == ""
    assert region.options == {}


@pytest.mark.basic
@pytest.mark.parametrize(
    ("name", "content", "options", "expected"),
    [
        pytest.param("", "", {}, "<!-- region: --><!-- endregion: -->", id="empty_region"),
        pytest.param(
            REGION_NAME,
            "",
            {"fold": "true"},
            create_region_content(REGION_NAME, "", with_options="fold='true'"),
            id="empty_content_with_options",
        ),
        pytest.param("test", "\n\n\n", {}, "<!-- region:test -->\n\n\n<!-- endregion:test -->", id="multiple_newlines"),
        pytest.param(
            REGION_NAME,
            CONTENT,
            {"a": "'quoted'"},
            create_region_content(REGION_NAME, CONTENT, with_options="a=\"'quoted'\""),
            id="quoted_option_values",
        ),
        pytest.param(
            "test-name",
            CONTENT,
            {"key-with-dashes": "value-with-dashes"},
            create_region_content("test-name", CONTENT, with_options="key-with-dashes='value-with-dashes'"),
            id="names_with_dashes",
        ),
        pytest.param(
            "test",
            "content with <!-- region:other -->",
            {},
            create_region_content(REGION_NAME, "content with <!-- region:other -->"),
            id="content_with_region_markers",
        ),
    ],
)
def test_region_str_representation(name: str, content: str, options: dict[str, str], expected: str) -> None:
    """Test string representation of extended regions.

    Tests that RegionExtended properly combine pre_string, post_string,
    and the main region content into the expected string format.

    :param name: Region name to test
    :param content: Main region content
    :param options: Region options
    :param expected: Expected combined string output
    """
    region = Region(name=name, content=content, options=options)
    assert str(region) == expected


@pytest.mark.basic
@pytest.mark.parametrize(
    ("name", "content", "options", "pre_string", "post_string", "expected"),
    [
        pytest.param(
            "test",
            CONTENT,
            {},
            "\n\n",
            "\n\n",
            "\n\n" + create_region_content(REGION_NAME, CONTENT) + "\n\n",
            id="surrounding_newlines",
        ),
        pytest.param(
            "test",
            CONTENT,
            {},
            "<!-- region:other -->",
            "<!-- endregion:other -->",
            create_region_content("other", create_region_content(REGION_NAME, CONTENT)),
            id="surrounding_regions",
        ),
        pytest.param("test", "", {}, "", "", "<!-- region:test --><!-- endregion:test -->", id="empty_everything"),
    ],
)
def test_region_extended_str_representation(
    name: str,
    content: str,
    options: dict[str, str],
    pre_string: str,
    post_string: str,
    expected: str,
) -> None:
    region = RegionExtended(name=name, content=content, options=options, pre_string=pre_string, post_string=post_string)
    assert str(region) == expected


@pytest.mark.basic
@pytest.mark.parametrize(
    ("file_content", "region_name", "expected_count", "expected_content"),
    [
        pytest.param(create_region_content(REGION_NAME, CONTENT), "test", 1, CONTENT, id="single_region"),
        pytest.param(
            create_region_content(
                REGION_NAME,
                "\ncontent1\n",
            )
            + create_region_content(
                REGION_NAME,
                "\ncontent2\n",
            ),
            "test",
            2,
            ["\ncontent1\n", "\ncontent2\n"],
            id="multiple_regions",
        ),
        pytest.param(
            create_region_content(REGION_NAME, CONTENT, with_options="key='value'"),
            "test",
            1,
            CONTENT,
            id="region_with_options",
        ),
        pytest.param(f"<!--region:test-->{CONTENT}<!--endregion:test-->", "test", 1, CONTENT, id="no_spaces_in_tags"),
    ],
)
def test_get_region(
    file_content: str,
    region_name: str,
    expected_count: int,
    expected_content: Union[str, list[str], None],
) -> None:
    regions = get_region(file_content, region_name)
    assert len(regions) == expected_count
    if expected_count > 0:
        if isinstance(expected_content, list):
            assert [r.content for r in regions] == expected_content
        else:
            assert regions[0].content == expected_content


@pytest.mark.basic
@pytest.mark.parametrize(
    ("file_content", "region_name"),
    [
        pytest.param(None, "test", id="none_content"),
        pytest.param("content", None, id="none_region_name"),
        pytest.param(123, "test", id="non_string_content"),
        pytest.param("content", 123, id="non_string_region_name"),
        pytest.param({"content": "test"}, "test", id="dict_content"),
    ],
)
def test_invalid_inputs(file_content: Any, region_name: Any) -> None:
    with pytest.raises(TypeError):
        get_region(file_content, region_name)  # type: ignore


@pytest.mark.basic
@pytest.mark.parametrize(
    "malformed_content",
    [
        pytest.param("<!-- region:test -->", id="missing_end_tag"),
        pytest.param("<!-- endregion:test -->", id="missing_start_tag"),
        pytest.param("<!-- region:test -->\n<!-- region:test -->", id="duplicate_start_tags"),
        pytest.param("<!-- region:test -->\n<!-- endregion:wrong -->", id="mismatched_names"),
        pytest.param("<!-- region test -->\n<!-- endregion:test -->", id="invalid_start_format"),
        pytest.param("<!-- region:test -->\n<!-- endregion test -->", id="invalid_end_format"),
    ],
)
def test_malformed_regions(malformed_content: str) -> None:
    """Test handling of malformed region markers."""
    regions = get_region(malformed_content, "test")
    assert len(regions) == 0


@pytest.mark.formatting
def test_special_characters() -> None:
    """Test handling of special characters in content and options."""
    region = Region(
        name="special", content="Content with \n\t\r\b\f chars", options={"key": "value with \n\t\r\b\f chars"}
    )
    result = str(region)
    assert "<!-- region:special" in result
    assert "<!-- endregion:special -->" in result


@pytest.mark.formatting
def test_unicode_handling() -> None:
    """Test handling of Unicode characters."""
    region = Region(
        name="unicode", content="Content with 🚀 emoji and 日本語", options={"key": "value with 🚀 and 日本語"}
    )
    result = str(region)
    assert "🚀" in result
    assert "日本語" in result


@pytest.mark.formatting
def test_multiple_regions_same_name() -> None:
    """Test handling of multiple regions with the same name."""
    content = (
        "<!-- region:test -->\ncontent1\n<!-- endregion:test -->\n"
        "middle\n"
        "<!-- region:test -->\ncontent2\n<!-- endregion:test -->"
    )
    regions = get_region(content, "test")
    assert len(regions) == 2
    assert [r.content for r in regions] == ["\ncontent1\n", "\ncontent2\n"]
    assert regions[1].pre_string == "\nmiddle\n"


@pytest.mark.error_handling
def test_invalid_region_name_format() -> None:
    """Test invalid region name formats."""
    invalid_names = [
        "test space",
        "test!@#",
        "test/slash",
        "",
    ]
    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid region name format"):
            get_region("content", name)


@pytest.mark.error_handling
@pytest.mark.parametrize(
    ("input_value", "error_message"),
    [
        (None, "'region_name' must be a string"),
        (123, "'region_name' must be a string"),
        ({}, "'region_name' must be a string"),
    ],
)
def test_invalid_inputs_with_specific_errors(input_value: Any, error_message: str) -> None:
    with pytest.raises(TypeError, match=error_message):
        get_region("content", input_value)  # type: ignore


@pytest.mark.error_handling
def test_nested_regions() -> None:
    """Test handling of nested region markers."""
    content = """
    <!-- region:outer -->
    outer content
    <!-- region:inner -->
    inner content
    <!-- endregion:inner -->
    more outer content
    <!-- endregion:outer -->
    """
    outer_regions = get_region(content, "outer")
    assert len(outer_regions) == 1
    inner_regions = get_region(outer_regions[0].content, "inner")
    assert len(inner_regions) == 1


@pytest.mark.error_handling
@pytest.mark.parametrize(
    "whitespace_variant",
    [
        "<!-- region:test-->",
        "<!--region:test -->",
        "<!--    region:test    -->",
        "<!-- region:test\t-->",
    ],
)
def test_whitespace_variations(whitespace_variant: str) -> None:
    """Test handling of different whitespace variations in tags."""
    content = f"{whitespace_variant}{CONTENT}<!-- endregion:test -->"
    regions = get_region(content, "test")
    assert len(regions) == 1


@pytest.mark.memory
def test_concurrent_access() -> None:
    """Test concurrent access to cached patterns."""

    def worker() -> None:
        content = create_region_content(REGION_NAME, CONTENT)
        regions = get_region(content, REGION_NAME)
        assert len(regions) == 1

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


@pytest.mark.memory
@pytest.mark.parametrize(
    "content_size",
    [0, 1, 100, 1000, 10_000],
)
def test_content_size_boundaries(content_size: int) -> None:
    """Test various content sizes."""
    content = "x" * content_size
    region = Region(name="test", content=content)
    result = str(region)
    assert len(result) > content_size


@pytest.mark.memory
def test_memory_usage() -> None:
    """Test memory usage with large content."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    large_content = "x" * LARGE_CONTENT_SIZE
    get_region(large_content, REGION_NAME)

    peak_memory = process.memory_info().rss
    memory_increase = peak_memory - initial_memory

    # Shouldn't use more than 2x the content size
    assert memory_increase < LARGE_CONTENT_SIZE * 2


@pytest.mark.performance
def test_performance_large_content() -> None:
    """Test performance with large content."""
    large_content = "x" * LARGE_CONTENT_SIZE
    start_time = time.perf_counter()
    get_region(large_content, "test")
    duration = time.perf_counter() - start_time
    assert duration < LARGE_CONTENT_TIMEOUT


@pytest.mark.benchmark
def test_performance_benchmark(benchmark: Any) -> None:
    """Benchmark performance of region parsing."""
    content = create_region_content(REGION_NAME, "x" * 1000)

    def run_benchmark() -> None:
        regions = get_region(content, REGION_NAME)
        assert len(regions) == 1

    benchmark(run_benchmark)


@pytest.mark.doctest
def test_docstring_examples() -> None:
    """Test that docstring examples work as documented."""
    import doctest

    import text_region_parser.region_parser as region_parser_module

    results = doctest.testmod(region_parser_module)
    assert results.failed == 0
