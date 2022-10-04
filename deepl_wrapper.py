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
import json
from typing import List


class DeepL:

    class ApiUrls:
        base_url = "https://api-free.deepl.com/v2"
        translate = f"{base_url}/translate"
        usage = f"{base_url}/usage"
        languages = f"{base_url}/languages?type=target"

    def __init__(self, api_token: str, user_agent: str, aiohttp_session: aiohttp.ClientSession):
        self._api_token = api_token
        self._user_agent = user_agent
        self._session = aiohttp_session
        self.supported_languages_abbr = self.read_language_abbreviations()

    @staticmethod
    def read_language_abbreviations() -> List[str]:
        try:
            with open("supported_languages.json", "r") as languages_file:
                content = json.load(languages_file)
                return [d["language"] for d in content]
        except json.JSONDecodeError:
            print("Supported languages file does not exist! Languages must be parsed manually.")
            return []

    def is_supported_language(self, abbreviation: str):
        return abbreviation in self.supported_languages_abbr

    async def _request_deepl_api(self, url, params: dict = None, **kwargs) -> dict:
        headers = {"Authorization": f"DeepL-Auth-Key {self._api_token}", "User-Agent": self._user_agent}

        async with self._session.get(url, headers=headers, params=params, **kwargs) as response:
            return await response.json(encoding="utf-8")

    async def get_supported_languages(self) -> dict:
        return await self._request_deepl_api(self.ApiUrls.languages)

    async def get_usage(self) -> dict:
        return await self._request_deepl_api(self.ApiUrls.usage)

    async def translate_text(self, text: str, target_language: str, source_language: str = None) -> List[str]:
        if not target_language:
            raise ValueError("Target language must be provided.")
        if not self.is_supported_language(target_language):
            raise ValueError(f"Target language {target_language} is not supported.")
        if source_language and not self.is_supported_language(source_language):
            raise ValueError(f"Source language {source_language} is not supported.")

        params = dict(text=text, target_lang=target_language)
        if source_language:
            params["source_lang"] = source_language
        response = await self._request_deepl_api(self.ApiUrls.translate, params=params, timeout=5)
        print(response)
        serialized_translations = response["translations"]
        translations = []
        for translation in serialized_translations:
            source_language = translation["detected_source_language"]
            translations.append(f"`{source_language} -> {target_language}`: {translation['text']}")

        return translations
