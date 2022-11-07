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


from typing import Optional
from .models import Translation as TranslationPayload
from .language import Language


class Translation:
    """
    An object representing a translation received from DeepL API.
    """

    def __init__(self, payload: TranslationPayload) -> None:
        self.detected_source_language = payload["detected_source_language"]
        self.text = payload["text"]
        # Below attributes cannot be directly fetched from the payload
        # -> Need to use separate finalization method!
        self.source_language: Optional[Language] = None
        self.target_language: Optional[Language] = None

    def finalize(self, source_language: Language, target_language: Language) -> None:
        """
        Finalize a translation to a complete object containing also source and target languages. Should be called only
        internally.
        :param source_language: Source language of the translation.
        :param target_language: Target language of the translation.
        :exception ValueError: Either source language or target language has a falsy value.
        """
        if not source_language:
            raise ValueError("Source language must be provided.")
        if not target_language:
            raise ValueError("Target language must be provided.")

        self.source_language = source_language
        self.target_language = target_language
