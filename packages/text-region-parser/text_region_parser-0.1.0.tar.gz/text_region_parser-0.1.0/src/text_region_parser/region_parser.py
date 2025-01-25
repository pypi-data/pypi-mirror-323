"""Region parser.

This module contains the logic to parse the regions in the README.md (or other text/MarkDown) file.
"""

import logging
import re
from typing import Optional

from text_region_parser._utils import _end_region_pattern, _get_region_validate_inputs, _region_pattern
from text_region_parser.options import option_parser
from text_region_parser.region_class import RegionExtended

logger = logging.getLogger(__name__)

__all__ = ("get_region",)


def get_region(file_content: str, region_name: str) -> list[RegionExtended]:
    r"""Get the region from the file.

    Example:
        >>> text = '''
        ... Some text
        ... <!-- region:example key=value -->
        ... Region content
        ... <!-- endregion:example -->
        ... More text
        ... '''
        >>> region_list = get_region(text, "example")
        >>> len(region_list)
        1
        >>> region_list[0].content
        '\nRegion content\n'


    :param file_content: The content of the Markdown/text file.
    :param region_name: The name of the region to get (must match ^[\w-]+$).
    :return: The list of regions in the file.
    :raises TypeError: If inputs aren't strings.
    :raises ValueError: If the `region_name` format is invalid.
    """
    _get_region_validate_inputs(file_content, region_name)
    if not file_content or not region_name:
        return []

    not_content: str = ""
    regions: list[RegionExtended] = []

    pattern = _region_pattern(region_name)
    pattern_with_opt = _region_pattern(region_name, with_options=True)
    end_pattern = _end_region_pattern(region_name)

    found: list[str] = pattern.findall(file_content)
    split: list[str] = pattern.split(file_content)

    for index, section in enumerate(split):
        # If this is a first string, then add it to result as start of a sequence
        if index == 0:
            not_content = section
            continue

        start_tag_str = found[index - 1]
        start_tag: Optional[re.Match[str]] = pattern_with_opt.match(start_tag_str)

        # If we can't find a closing tag, then this is an invalid region
        end_search = end_pattern.search(section)
        if not end_search or not start_tag:
            not_content = start_tag_str + section
            continue

        content: str = ""
        end: str
        end_split: list[str] = end_pattern.split(section, 1)
        if len(end_split) == 2:
            content, end = end_split
        else:
            end = end_split[0]

        regions.append(
            RegionExtended(
                name=region_name,
                content=content,
                options=option_parser(start_tag.group("opt") or ""),
                pre_string=not_content,
                post_string="",
            )
        )
        not_content = end

    if not regions:
        return regions

    if not_content:
        regions[-1].post_string = not_content

    return regions
