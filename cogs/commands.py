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

from discord.ext import commands
from translator_bot import TranslatorBot


class TranslationCog(commands.Cog):

    def __init__(self, bot: TranslatorBot):
        self.bot = bot

    @commands.guild_only()
    @commands.hybrid_command(name="translate", description="Translate text to english.", aliases=["t"])
    async def translate(self, ctx: commands.Context, *, text: str) -> None:
        """
        Translate text to English.

        :param ctx:
        :param text: Text to translate. Source language is detected automatically.
        """
        try:
            translations = await self.bot.deepl.translate_text(text, "EN-US")
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
            translations = await self.bot.deepl.translate_text(text, target_language=target_language.upper())
            await ctx.send("\n".join(translations))
        except ValueError as e:
            await ctx.send(str(e))

    @commands.guild_only()
    @commands.hybrid_command(name="languages", description="Get list of all supported language abbreviations.")
    async def get_supported_languages(self, ctx: commands.Context):
        formatted = [f"`{abbr}`" for abbr in self.bot.deepl.supported_languages_abbr]
        await ctx.send(", ".join(formatted))


# noinspection PyTypeChecker
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TranslationCog(bot))
