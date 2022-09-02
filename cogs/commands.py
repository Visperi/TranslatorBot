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

import json
from discord.ext import commands
from translator_bot import TranslatorBot
from typing import List


class TranslationCog(commands.Cog):

    base_url = "https://api-free.deepl.com/v2"

    def __init__(self, bot: TranslatorBot):
        self.bot = bot
        self.supported_languages_abbr = self.read_language_abbreviations()

    @classmethod
    async def request_deepl_api(cls, bot: TranslatorBot, url: str, params: dict = None) -> str:
        headers = dict()
        headers["Authorization"] = f"DeepL-Auth-Key {bot.deepl_api_token}"
        headers["User-Agent"] = bot.name

        return await bot.fetch_url(url, headers=headers, params=params)

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

    async def __translate_text(self, text: str, source_language: str = None,
                               target_language: str = "EN-US") -> List[str]:
        params = dict()
        params["text"] = text
        params["target_lang"] = target_language.capitalize()
        if source_language:
            source_language = source_language.capitalize()
            if not self.is_supported_language(source_language):
                raise ValueError(f"Source language `{source_language}` is not supported.")
            params["source_lang"] = source_language
        if not self.is_supported_language(target_language):
            raise ValueError(f"Target language `{target_language}` is not supported.")

        response = await self.request_deepl_api(self.bot, self.base_url + "/translate", params=params)
        print(response)
        serialized_translations = json.loads(response)["translations"]
        translations = []
        for translation in serialized_translations:
            source_language = translation["detected_source_language"]
            translations.append(f"`{source_language} -> {target_language}`: {translation['text']}")

        return translations

    @commands.guild_only()
    @commands.hybrid_command(name="translate", description="Translate text to english.", aliases=["t"])
    async def translate(self, ctx: commands.Context, *, text: str) -> None:
        """
        Translate text to English.

        :param ctx:
        :param text: Text to translate. Source language is detected automatically.
        """
        try:
            translations = await self.__translate_text(text)
            await ctx.send("\n".join(translations))
        except ValueError as e:
            await ctx.send(str(e))

    @commands.guild_only()
    @commands.hybrid_command(name="ttranslate", description="Translate text to a target language.",
                             aliases=["target_translate", "tt"])
    async def target_translate(self, ctx: commands.Context, target_language: str, *, text: str) -> None:
        """
        Translate text to a target language.

        :param ctx:
        :param target_language: Target language for the translation. Must be and abbreviation. Case-insensitive.
        :param text: Text to translate. Source language is detected automatically.
        """
        try:
            translations = await self.__translate_text(text, target_language=target_language)
            await ctx.send("\n".join(translations))
        except ValueError as e:
            await ctx.send(str(e))

    @commands.command(name="languages", description="Get list of all supported language abbreviations.")
    async def get_supported_languages(self, ctx: commands.Context):
        formatted = [f"`{abbr}`" for abbr in self.supported_languages_abbr]
        await ctx.send(", ".join(formatted))


# noinspection PyTypeChecker
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TranslationCog(bot))
