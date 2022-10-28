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

import discord
import re
import traceback
import sys
import datetime
from discord.ext import commands
from translator_bot import TranslatorBot
from deepl.errors import *


class EventListenerCog(commands.Cog):
    """
    A cog handling different Discord events apart from command exceptions.
    """

    def __init__(self, bot: TranslatorBot):
        self.bot = bot

    async def __translate_from_reply(self, message: discord.Message) -> None:
        """
        Translate a message from a replied message. Is triggered only when the bot is mentioned.
        :param message: Message which triggered this event.
        """
        split = message.content.split()
        if len(split) > 2:
            await message.channel.send("Please send only the possible non-English target language after mentioning me.")
            return
        try:
            target_language = split[1]
        except IndexError:
            target_language = "EN-US"

        untranslated_text = message.reference.resolved.content
        try:
            translated = await self.bot.deepl_client.translate(untranslated_text, target_language)
            await message.reply("\n".join(translated), mention_author=False)
        except DeepLError as e:
            await message.channel.send(str(e))
        except Exception as e:
            ts = datetime.datetime.now().replace(microsecond=0)
            print(f"[{ts}] Ignoring unexpected exception:", file=sys.stderr)
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            print()

            await message.channel.send(f"Unexpected error: `{type(e).__name__}`. Contact the bot owner to resolve "
                                       f"this issue.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message, /) -> None:
        if message.author == self.bot.user:
            return

        try:
            startswith_mention = re.fullmatch(rf"<@!?{self.bot.user.id}>", message.content.split()[0])
            is_quick_translation = startswith_mention and message.reference
        except IndexError:
            startswith_mention = False
            is_quick_translation = False

        # Attempt to translate only if the message contains mention of this bot and a replied message reference
        if is_quick_translation:
            await self.__translate_from_reply(message)
        elif startswith_mention:
            await message.channel.send("Translate a message with a mention by also replying to "
                                       "the translated message.")
        else:
            await self.bot.process_commands(message)


async def setup(bot: TranslatorBot):
    await bot.add_cog(EventListenerCog(bot))
