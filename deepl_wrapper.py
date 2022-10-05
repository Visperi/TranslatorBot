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

import aiohttp
import asyncio
from typing import List, Optional


class DeepLApiError(Exception):
    """
    An exception for DeepL API related request errors.
    """
    pass


class DeepL:

    class ApiUrls:
        base_url = "https://api-free.deepl.com/v2"
        translate = f"{base_url}/translate"
        usage = f"{base_url}/usage"
        languages = f"{base_url}/languages?type=target"

    class Language:
        def __init__(self, raw: dict):
            self.abbreviation: str = raw["language"]
            self.name: str = raw["name"]
            self.supports_formality: bool = raw["supports_formality"]

        def as_dict(self) -> dict:
            return dict(language=self.abbreviation, name=self.name, supports_formality=self.supports_formality)

    def __init__(self, api_token: str, user_agent: str, aiohttp_session: aiohttp.ClientSession):
        self._api_token = api_token
        self._user_agent = user_agent
        self._session = aiohttp_session
        self._supported_languages: List['DeepL.Language'] = []
        asyncio.create_task(self.__set_supported_languages())

    @property
    def supported_languages(self) -> List['DeepL.Language']:
        return self._supported_languages

    async def __set_supported_languages(self) -> None:
        """
        Fetch and set supported languages.
        """
        tmp = await asyncio.gather(self.fetch_supported_languages())
        self._supported_languages = tmp[0]

    @staticmethod
    def replace_aliases(representation: str, ignore_case: bool = False) -> str:
        """
        Replace aliases in a language representation string.
        :param representation: A string representing a supported language.
        :param ignore_case: Ignore case for the alias comparison.
        :return: Language string representation with aliases converted to supported syntax.
        """
        if ignore_case:
            if representation.casefold() == "en" or representation.casefold() == "english":
                return "EN-US"
        else:
            if representation == "EN" or representation == "English":
                return "EN-US"

        return representation

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

        representation = self.replace_aliases(representation, ignore_case=ignore_case)

        if ignore_case:
            representation = representation.casefold()
        for language in self.supported_languages:
            lang_name = language.name
            lang_abbr = language.abbreviation
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

    async def fetch_supported_languages(self) -> List[Language]:
        """
        Fetch supported language data from the DeepL API.
        :return: List of Language objects.
        """
        languages = []
        for raw in await self._request_deepl_api(self.ApiUrls.languages):
            languages.append(self.Language(raw))

        return languages

    async def _request_deepl_api(self, url: str, params: dict = None, timeout: int = 5, **kwargs) -> dict:
        """
        Fetch data from DeepL API.
        :param url: DeepL API url to fetch data from.
        :param params: Params needed for the API request.
        :param timeout: Timeout for the request in seconds.
        :param kwargs: Kwargs for aiohttp.ClientSession.get() method.
        :return: DeepL API response in JSON.
        :raises DeepLApiError: If there are too many frequent API requests or the API quota is exceeded.
        """
        headers = {"Authorization": f"DeepL-Auth-Key {self._api_token}", "User-Agent": self._user_agent}

        async with self._session.get(url, headers=headers, params=params, timeout=timeout, **kwargs) as response:
            if response.status == 429:
                raise DeepLApiError("Too many DeepL API requests. Consider adding some delay between frequent "
                                    "requests.")
            elif response.status == 456:
                raise DeepLApiError("DeepL API quota exceeded. This can be resolved by upgrading DeepL subscription.")
            response.raise_for_status()

            return await response.json(encoding="utf-8")

    async def get_usage(self) -> dict:
        """
        Get the monthly usage status of DeepL API account.
        :return: Dictionary containing the usage data.
        """
        return await self._request_deepl_api(self.ApiUrls.usage)

    async def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> List[str]:
        """
        Translate text from source language to target language.
        :param text: Text to translate.
        :param target_language: Target language to translate the text to.
        :param source_language: Source language for the original text. If omitted, the source language is detected
        automatically.
        :return: List of translated texts.
        """
        target_lang = self.get_language(target_language, ignore_case=True)
        if not target_lang:
            raise ValueError(f"Target language {target_language} is not supported.")
        if source_language and not self.get_language(source_language, ignore_case=True):
            raise ValueError(f"Target source language {source_language} is not supported.")

        params = dict(text=text, target_lang=target_lang.abbreviation)
        if source_language:
            # Get language, then split possible EN-US, EN-GB languages to only EN (only this is supported as source)
            params["source_lang"] = self.get_language(source_language, ignore_case=True).abbreviation.split("-")[0]
        response = await self._request_deepl_api(self.ApiUrls.translate, params=params)
        print(response)
        serialized_translations = response["translations"]
        translations = []
        for translation in serialized_translations:
            detected_source_language = self.get_language(translation["detected_source_language"])
            translations.append(f"`{detected_source_language.abbreviation} -> {target_lang.abbreviation}`: "
                                f"{translation['text']}")

        return translations
