import functools
import re
from typing import get_type_hints


@functools.cache
def _region_pattern(region_name: str, with_options: bool = False) -> re.Pattern[str]:
    """Return the pattern for a region.

    :param region_name: The name of the region.
    :return: The pattern for the region.
    """
    region_name = re.escape(region_name)
    if with_options:
        return re.compile(rf"<!--\s*?region:{region_name}(?P<opt>.*?)-->", flags=re.MULTILINE)
    return re.compile(rf"<!--\s*?region:{region_name}.*?-->", flags=re.MULTILINE)


@functools.cache
def _end_region_pattern(region_name: str) -> re.Pattern[str]:
    """Return the pattern for a region.

    :param region_name: The name of the region.
    :return: The pattern for the region.
    """
    region_name = re.escape(region_name)
    return re.compile(rf"<!--\s*?endregion:{region_name}\s*?-->", flags=re.MULTILINE)


def _validate_region_name(region_name: str) -> None:
    """Validate the region name.

    :param region_name: The name of the region.
    :raises ValueError: If the region name is invalid.
    """
    if not isinstance(region_name, str):
        raise TypeError("Region name must be a string")
    if not re.match(r"^[\w-]+$", region_name):
        raise ValueError("Invalid region name format")


def _get_region_validate_inputs(file_content: str, region_name: str) -> None:
    """Validate the inputs of the get_region function.

    :param file_content: The content of the Markdown/text file.
    :param region_name: The name of the region to get.
    :return: If returns None, then the inputs are invalid.
    Otherwise, returns the list of regions.
    :raises ValueError: If the region name is invalid.
    :raises TypeError: If the file content or region name is not a string.
    """
    if not isinstance(region_name, str):
        raise TypeError("'region_name' must be a string")
    if not isinstance(file_content, str):
        raise TypeError("'file_content' must be a string")

    _validate_region_name(region_name)


def _validate_options_type(options_type: type[dict]) -> None:
    """Validate that all TypedDict values are strings.

    :param options_type: TypedDict type to validate, not an instance or simple dict.
    :raises TypeError: If options_type is invalid.
    """
    if not (isinstance(options_type, type) and hasattr(options_type, "__annotations__")):
        raise TypeError("options_type must be a TypedDict subclass")

    hints = get_type_hints(options_type)
    if not all(hint is str for hint in hints.values()):
        raise TypeError("All TypedDict values must be of type str")
