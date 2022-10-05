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


class TranslationCog(commands.Cog, name="Translations",
                     description="Commands for doing translations in Discord chat."):
    """
    A cog encapsulating various translation commands utilizing DeepL API.
    """

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
        except Exception as e:
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
            translations = await self.bot.deepl.translate_text(text, target_language=target_language)
            await ctx.send("\n".join(translations))
        except Exception as e:
            await ctx.send(str(e))

    @commands.guild_only()
    @commands.hybrid_command(name="stranslate", aliases=["source_translate", "st"],
                             description="Translate text from source language to target language. "
                                         "Both source and target language are needed.")
    async def source_translate(self, ctx: commands.Context, source_language: str, target_language: str, *, text: str) \
            -> None:
        """
        Translate text from source language to target language. Both source and target languages are required.
        :param ctx:
        :param source_language: Source language for the original text.
        :param target_language: Target language for the translated text.
        :param text: Text to translate.
        """
        try:
            translations = await self.bot.deepl.translate_text(text, target_language, source_language=source_language)
            await ctx.send("\n".join(translations))
        except Exception as e:
            await ctx.send(str(e))

    @commands.guild_only()
    @commands.hybrid_command(name="languages", description="Get list of all supported language abbreviations.")
    async def get_supported_languages(self, ctx: commands.Context):
        """
        Get list of supported languages and their abbreviations. Both abbreviation and full langauge names are
        compatible with translation commands.
        """
        supported_languages = []
        for language in self.bot.deepl.supported_languages:
            supported_languages.append(f"`{language.abbreviation}`: {language.name}")
        await ctx.send("\n".join(supported_languages))


# noinspection PyTypeChecker
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TranslationCog(bot))