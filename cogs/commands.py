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


class TranslationCog(commands.Cog):

    def __init__(self, bot: TranslatorBot):
        self.bot = bot
        self.translation_url = "https://api-free.deepl.com/v2/translate"

    @commands.guild_only()
    @commands.hybrid_command(name="translate", description="Translate a message.")
    async def translate(self, ctx: commands.Context, *, text: str) -> None:
        target_language = "EN"
        headers, params = dict(), dict()
        headers["Authorization"] = f"DeepL-Auth-Key {self.bot.deepl_api_token}"
        headers["User-Agent"] = self.bot.name
        params["text"] = text
        params["target_lang"] = target_language

        response = await self.bot.fetch_url(self.translation_url, headers=headers, params=params)
        print(response)
        translations = json.loads(response)["translations"]
        concatenated_translations = []
        for translation in translations:
            source_language = translation["detected_source_language"]
            concatenated_translations.append(f"{source_language} -> {target_language}: {translation['text']}")

        await ctx.send("\n".join(concatenated_translations))


# noinspection PyTypeChecker
async def setup(bot: commands.Bot):
    await bot.add_cog(TranslationCog(bot))
