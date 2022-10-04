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
        self.supported_languages: List['DeepL.Language'] = []
        asyncio.create_task(self.__get_supported_languages())

    async def __get_supported_languages(self):
        asd = await asyncio.gather(self.fetch_supported_languages())
        self.supported_languages = asd[0]

    @staticmethod
    def replace_aliases(search: str, ignore_case: bool = False) -> str:
        if ignore_case:
            if search.casefold() == "en" or search.casefold() == "english":
                return "EN-US"
        else:
            if search == "EN" or search == "English":
                return "EN-US"

        return search

    def get_language(self, search: str, ignore_case: bool = False) -> Optional[Language]:
        if not search:
            raise ValueError("Target language must be provided.")

        search = self.replace_aliases(search, ignore_case=ignore_case)

        if ignore_case:
            search = search.casefold()
        for language in self.supported_languages:
            lang_name = language.name
            lang_abbr = language.abbreviation
            if ignore_case:
                lang_name = lang_name.casefold()
                lang_abbr = lang_abbr.casefold()
            if search == lang_name or search == lang_abbr:
                return language

        return None

    def is_supported_language(self, search: str, ignore_case: bool = False) -> bool:
        if not search:
            return False

        return self.get_language(search, ignore_case=ignore_case) is not None

    async def fetch_supported_languages(self) -> List[Language]:
        languages = []
        for raw in await self._request_deepl_api(self.ApiUrls.languages):
            languages.append(self.Language(raw))

        return languages

    async def _request_deepl_api(self, url, params: dict = None, timeout: int = 5, **kwargs) -> dict:
        headers = {"Authorization": f"DeepL-Auth-Key {self._api_token}", "User-Agent": self._user_agent}

        async with self._session.get(url, headers=headers, params=params, timeout=timeout, **kwargs) as response:
            if response.status == 429:
                raise DeepLApiError("Too many DeepL API requests. Consider adding some delay between frequent "
                                    "requests.")
            elif response.status == 456:
                raise DeepLApiError("DeepL API quota exceeded. This can be resolved by upgrading DeepL subscription.")
            return await response.json(encoding="utf-8")

    async def get_usage(self) -> dict:
        return await self._request_deepl_api(self.ApiUrls.usage)

    async def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> List[str]:
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
