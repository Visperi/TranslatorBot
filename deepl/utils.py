"""
MIT License

Copyright (c) 2022 Niko Mätäsaho

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Dict, List
import logging


def replace_aliases(representation: str, ignore_case: bool = False) -> str:
    """
    Replace aliases in a language representation string.

    :param representation: A string representing a supported language.
    :param ignore_case: Ignore case for the alias comparison.
    :return: Language string representation with aliases converted to supported syntax. Returns the original
    representation if no aliases are found.
    """
    # TODO: Which English and Portuguese to prefer here?
    aliases: Dict[str, List[str]] = {
        "EN-US": ["EN", "English"],
        "PT-PT": ["PT", "Portuguese"],
        "ZH": ["Chinese"]
    }

    if not representation:
        raise ValueError("Language representation must be provided.")

    lookup = representation
    if ignore_case:
        lookup = representation.casefold()

    for language_code, language_aliases in aliases.items():
        if ignore_case:
            language_aliases = [alias.casefold() for alias in language_aliases]
        if lookup in language_aliases:
            return language_code

    return representation


def strip_source_language_exceptions(representation: str, ignore_case: bool = False) -> str:
    """
    Strip out possible parts from a language representation that are only usable in a target language. Replaces also
    aliases, but returns the original representation if nothing needs to be stripped.

    :param representation: A string representing a supported language.
    :param ignore_case: Ignore case for the alias comparison and stripping.
    :return: Language representation with aliases replaced and invalid source language parts stripped.
    The original representation is returned instead if nothing needs to be replaced.
    :exception ValueError: The representation has a falsy value.
    """
    exceptions = [
        "PT-BR",
        "PT-PT",
        "EN-US",
        "EN-GB"
    ]

    lookup = replace_aliases(representation, ignore_case=ignore_case)
    if ignore_case:
        exceptions = [exc.casefold() for exc in exceptions]
        lookup = lookup.casefold()

    if lookup in exceptions:
        return representation.split("-")[0].upper()

    return representation


class _CustomFormatter(logging.Formatter):
    """
    A default log formatter with colours.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    output_format = "[{asctime}] [{levelname:<8}] {name}: {message}"

    LEVEL_COLOURS = [
        (logging.DEBUG, grey),
        (logging.INFO, grey),
        (logging.WARNING, yellow),
        (logging.ERROR, red),
        (logging.CRITICAL, bold_red)
    ]

    FORMATTERS = {}
    for level, colour in LEVEL_COLOURS:
        FORMATTERS[level] = logging.Formatter(fmt=colour+output_format+reset, datefmt="%Y-%m-%d %H:%M:%S", style="{")

    def format(self, record) -> str:
        formatter = self.FORMATTERS.get(record.levelno, self.FORMATTERS[logging.DEBUG])

        if record.exc_info:
            formatted = formatter.formatException(record.exc_info)
            record.exc_text = self.red + formatted + self.reset

        output = formatter.format(record)
        record.exc_text = None
        return output


def configure_logging(
        level: int = logging.INFO,
        formatter: logging.Formatter = None,
        handler: logging.Handler = None,
        use_colours: bool = True) -> None:
    """
    Configure logging for the logging system.

    :param level: The smallest logging level to log.
    :param formatter: Formatter for the log messages. If omitted, a default one is set up with or without colours
    depending on parameter use_colours.
    :param handler: Handler for the logger. If omitted, StreamHandler is used with default parameters.
    :param use_colours: Choose if colour should be used for the logging. Has no effect if formatter is explicitly
    given to this function.
    """

    if not handler:
        handler = logging.StreamHandler()

    if not formatter and use_colours:
        formatter = _CustomFormatter()
    else:
        formatter = logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S",
                                      style="{")

    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
