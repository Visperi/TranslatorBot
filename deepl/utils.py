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

# TODO: Add global logging function here?
from typing import Dict, List


def replace_aliases(representation: str, ignore_case: bool = False) -> str:
    """
    Replace aliases in a language representation string.
    :param representation: A string representing a supported language.
    :param ignore_case: Ignore case for the alias comparison.
    :return: Language string representation with aliases converted to supported syntax. Returns the original
    representation if no aliases are found.
    """
    aliases: Dict[str, List[str]] = {
        "EN-US": ["EN", "English"],
        "PT-PT": ["PT", "Portuguese"],
        "ZH": ["Chinese"]
    }

    if ignore_case:
        representation = representation.casefold()

    for language_code, language_aliases in aliases.items():
        if ignore_case:
            language_aliases = [alias.casefold() for alias in language_aliases]
        if representation in language_aliases:
            return language_code

    return representation
