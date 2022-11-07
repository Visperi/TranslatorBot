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

from __future__ import annotations
from typing import List, Optional, Union, Tuple
from .language import Language
from .translation import Translation
from .errors import *
from . import utils
import aiohttp
import logging

_logger = logging.getLogger(__name__)


class Client:

    class ApiPath:
        translate = "/translate"
        usage = "/usage"
        languages = "/languages?type=target"

    def __init__(
            self,
            api_token: str, user_agent: str,
            aiohttp_session: aiohttp.ClientSession
    ) -> None:
        # utils.configure_logging()
        self._user_agent = user_agent
        self._session = aiohttp_session
        self._supported_languages: List[Language] = []

        self._api_token = api_token
        if api_token.endswith(":fx"):
            self._version = "free"
        else:
            self._version = "pro"

        _logger.info(f"Logging in using {self._version} version of DeepL token.")

    @property
    def supported_languages(self) -> List[Language]:
        return self._supported_languages

    @property
    def version(self) -> str:
        return self._version

    def get_language(self, representation: str, ignore_case: bool = False) -> Optional[Language]:
        """
        Convert a string representing language to an actual Language object.
        :param representation: String representing a language.
        :param ignore_case: Ignore case for the search of an actual Language object.
        :return: Language object if found from supported languages, None otherwise.
        :raises ValueError: If the target language is not provided.
        """
        if not representation:
            raise ValueError("Target language must be provided.")

        representation = utils.replace_aliases(representation, ignore_case=ignore_case)

        if ignore_case:
            representation = representation.casefold()
        for language in self.supported_languages:
            lang_name = language.name
            lang_abbr = language.language_code
            if ignore_case:
                lang_name = lang_name.casefold()
                lang_abbr = lang_abbr.casefold()
            if representation == lang_name or representation == lang_abbr:
                return language

        return None

    def is_supported_language(self, search: str, ignore_case: bool = False) -> bool:
        """
        Check if language is supported. If the language is also needed, get_language may be better method.
        :param search: Language to check for supported status.
        :param ignore_case: Ignore case for the check.
        :return: True if the language is supported, False otherwise.
        """
        if not search:
            return False

        return self.get_language(search, ignore_case=ignore_case) is not None

    async def update_supported_languages(self) -> List[Language]:
        """
        Update supported languages in the DeepL API.
        :return: List of supported languages as Language objects.
        """
        languages = []
        for raw in await self.__request_deepl_api(self.ApiPath.languages):
            languages.append(Language(raw))

        self._supported_languages = languages
        return languages

    async def __request_deepl_api(self,
                                  path: str,
                                  params: Union[dict, List[Tuple[str, str]]] = None,
                                  timeout: int = 5, **kwargs) -> dict:
        """
        Fetch data from DeepL API.
        :param path: DeepL API url to fetch data from.
        :param params: Params needed for the API request.
        :param timeout: Timeout for the request in seconds.
        :param kwargs: Kwargs for aiohttp.ClientSession.get() method.
        :return: DeepL API response in JSON.
        :raises DeepLApiError: If there are too many frequent API requests or the API quota is exceeded.
        """
        if self.version == "free":
            base_url = "https://api-free.deepl.com/v2/"
        else:
            base_url = "https://api.deepl.com/v2/"

        url = base_url + path.lstrip("/")
        headers = {"Authorization": f"DeepL-Auth-Key {self._api_token}", "User-Agent": self._user_agent}

        async with self._session.get(url, headers=headers, params=params, timeout=timeout, **kwargs) as response:

            if response.status == 429:
                raise TooManyRequestsError("Too many DeepL API requests. Consider adding some delay between frequent "
                                           "requests.")
            elif response.status == 456:
                raise DeepLQuotaExceededError("DeepL API quota exceeded. This can be resolved by upgrading DeepL "
                                              "subscription.")

            response_content = await response.json(encoding="utf-8")
            try:
                response.raise_for_status()

            except aiohttp.ClientResponseError:
                msg = response_content.get("message")
                _logger.exception(f"Error {response.status}: {msg}")

            else:
                return await response.json(encoding="utf-8")

    async def get_usage(self) -> dict:
        """
        Get the monthly usage status of DeepL API account.
        :return: Dictionary containing the usage data.
        """
        return await self.__request_deepl_api(self.ApiPath.usage)

    async def translate(
            self,
            text: Union[str, List[str]],
            target_language: str,
            source_language: Optional[str] = None) -> List[Translation]:
        """
        Translate text from source language to target language.
        :param text: Text to translate or list of texts to translate. Up to 50 translations is supported at once.
        :param target_language: Target language to translate the text to.
        :param source_language: Source language for the original text. If omitted, the source language is detected
        automatically.
        :return: List of translated texts.
        :exception ValueError: Text to translate has falsy value.
        :exception LanguageNotSupportedError: Target language or source language is not supported.
        """
        if not text:
            raise ValueError("Translated text must be provided.")
        if isinstance(text, list) and len(text) > 50:
            raise ValueError("Only up to 50 translations are supported at once.")

        target_lang = self.get_language(target_language, ignore_case=True)
        if not target_lang:
            raise LanguageNotSupportedError(f"Target language `{target_language}` is not supported.")
        if source_language and not self.get_language(source_language, ignore_case=True):
            raise LanguageNotSupportedError(f"Target source language `{source_language}` is not supported.")

        if isinstance(text, str):
            params = [("text", text)]
        else:
            params = [("text", untranslated) for untranslated in text]

        params.append(("target_lang", target_lang.language_code))

        if source_language:
            # Get language, then split possible EN-US, EN-GB languages to only EN (only this is supported as source)
            source_lang = self.get_language(source_language, ignore_case=True).language_code.split("-")[0]
            params.append(("source_lang", source_lang))

        response = await self.__request_deepl_api(self.ApiPath.translate, params=params)
        translations = [Translation(payload) for payload in response["translations"]]

        for translation in translations:
            translation.finalize(self.get_language(translation.detected_source_language), target_lang)

        return translations
