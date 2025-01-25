"""Region constructor.

This module provides a class for creating region parsers.
"""

import functools
import logging
from collections.abc import Callable
from os import PathLike
from pathlib import Path
from typing import Optional, TypeVar

from text_region_parser._utils import _validate_options_type, _validate_region_name
from text_region_parser.region_parser import get_region

__all__ = (
    "RegionConstructor",
    "InvalidOptionsError",
)


OptionType = TypeVar("OptionType", bound=type[dict])
ParserType = Callable[[OptionType], str]

logger = logging.getLogger(__name__)


class InvalidOptionsError(ValueError):
    """Raised when the options are invalid."""


# noinspection GrazieInspection
class RegionConstructor:
    """A class for creating and managing region parsers.

    This class provides functionality to parse and update regions in text files.
    It ensures safe file operations and proper error handling.

    Thread Safety:
        - Reading operations are thread-safe
        - Parser registration is not thread-safe
        - File operations should not be performed concurrently on the same file


    .. example-code::

        .. code-block:: python
            :linenos:
            from pathlib import Path
            from typing import TypedDict

            class ScopeOptions(TypedDict):
                name: str
                level: str

            constructor = RegionConstructor()

            @constructor.add_parser("scope", options_type=ScopeOptions)
            def create_scope_content(options: ScopeOptions) -> str:
                return f"Scope: {options['name']} with level {options['level']}"

            # Parse the content.
            file_path = Path("README.md")
            constructor.update_files_data(file_path)
            print(file_path.read_text())
    """

    def __init__(self) -> None:
        """Post-init script.

        Add a `_parser` container
        """
        self._parsers: dict[str, ParserType] = {}

    def add_parser(
        self,
        region_name: str,
        options_type: Optional[OptionType] = None,
    ) -> Callable[[ParserType], ParserType]:
        """Register a parser.

        :param region_name: The name of the region, which will be parsed.
        :param options_type: Exists for type annotations.
            Please note that the `options_type` must be a subclass of TypedDict with values of type `str`.
            This is because the `options` will be passed to the parser as a `TypedDict` instance.
        :return: A decorator for adding a parser.
        :raises TypeError: If one of the arguments has an invalid type.
        :raises ValueError: If the region name is invalid format.
        """
        _validate_region_name(region_name)
        if options_type:
            _validate_options_type(options_type)

        def decorator(parser: ParserType) -> ParserType:
            self._parsers[region_name] = parser

            @functools.wraps(parser)
            def wrapper(options: OptionType) -> str:
                if options_type and not isinstance(options, options_type):
                    raise ValueError(f"The options must be an instance of {options_type}")
                return parser(options)

            return wrapper

        return decorator

    def parse_content(self, content: str) -> str:
        """Parse content and replace regions' content.

        :param content: The content to parse.
        :return: The parsed content with new regions' data.
            If a parser fails or returns invalid data, the error is logged and the region is skipped.
        :raises TypeError: If content is not a string.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        for region_name, parser in self._parsers.items():
            regions = get_region(content, region_name)
            if not regions:
                continue

            for region in regions:
                try:
                    result = parser(region.options)
                    if not isinstance(result, str):
                        logger.error(f"Parser for region {region_name} returned {type(result).__name__} instead of str")
                        continue
                    region.content = result

                except InvalidOptionsError as e:
                    logger.error(f"Invalid options for region {region_name}: {e}")
                    continue

            content = "\n".join(str(region) for region in regions)

        return content

    def update_files_data(self, *file_paths: PathLike) -> None:
        """Parse a file and replace regions' content.

        :param file_paths: The paths of the files to parse and update.
        """
        for file_path in file_paths:
            path = Path(file_path)
            content = self.parse_content(path.read_text())
            path.write_text(content)
