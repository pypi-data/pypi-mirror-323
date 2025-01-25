"""Region classes."""

from dataclasses import dataclass, field

from text_region_parser import Options, make_string_from_options

__all__ = (
    "Region",
    "RegionExtended",
)


@dataclass
class Region:
    """Region type.

    :param name: Name of the region.
    :param content: The content of the region.
        Default: ""
    :param options: The options of the region.
        Default: {}
    """

    name: str
    content: str = field(default="")
    options: Options = field(default_factory=dict)
    # Consider using more specific types or TypedDict for options

    def __str__(self) -> str:
        """Return the string representation of the region.

        :return: The string representation of the region with the options and start/end "tags".
        """
        region_start = f"<!-- region:{self.name}"
        if self.options:
            region_start += f" {make_string_from_options(self.options)}"
        region_start += " -->"
        return f"{region_start}{self.content}<!-- endregion:{self.name} -->"


@dataclass
class RegionExtended(Region):
    """A class representing a region with extended content.

    :param pre_string: The string to be added before the region content (which is not part of the region/other regions).
        Default: ""
    :param post_string: The string to be added after the region content (which is not part of the region/other regions).
        Default: ""
    """

    pre_string: str = field(default="")
    post_string: str = field(default="")

    def __str__(self) -> str:
        """Return the string representation of the region.

        :return: The string representation of the region with the pre- and post- strings.
        """
        if not self.name:
            return self.pre_string + self.post_string

        region = super().__str__()
        if self.pre_string:
            region = self.pre_string + region
        if self.post_string:
            region += self.post_string
        return region
