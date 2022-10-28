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

import sys
import traceback
import datetime
from discord.ext import commands
from typing import List, Any, Union
from deepl.errors import *


class ErrorHandlerCog(commands.Cog):
    """
    A cog for handling exceptions raised during Discord command execution.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def __parse_missing(iterable: List[Any], separator: str = None) -> Union[List[str], str]:
        """
        Parse and format iterable items to a list of strings or a string joined with separator.

        :param iterable: Iterable which items to parse and format.
        :param separator: Separator to join the formatted strings with. If None, list of formatted strings is returned.
        :return: List of formatted strings or a single string joined wit separator
        """
        ret = [f"`{item}`" for item in iterable]
        if separator:
            ret = separator.join(ret)

        return ret

    @staticmethod
    def __log_unexpected_error(error: Exception):
        ts = datetime.datetime.now().replace(microsecond=0)
        print(f"[{ts}] Ignoring unexpected exception:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandInvokeError) -> None:
        try:
            original = error.original
        except AttributeError:
            # Some really unexpected error happened
            self.__log_unexpected_error(error)
            return

        if isinstance(original, commands.CommandNotFound) or isinstance(original, commands.MissingRequiredArgument):
            return

        if isinstance(original, commands.DisabledCommand):
            await ctx.send(f"Command `{ctx.command}` is currently disabled.")

        elif isinstance(original, commands.NoPrivateMessage):
            await ctx.send("This command is not supported in private messages.")

        elif isinstance(original, commands.PrivateMessageOnly):
            await ctx.send("This command is supported only in private messages.")

        # Permission exceptions
        elif isinstance(original, commands.NotOwner):
            await ctx.send("This command can be executed only by the bot owner.")

        elif isinstance(original, commands.MissingPermissions):
            missing = self.__parse_missing(original.missing_permissions, ", ")
            await ctx.send(f"Sorry, you are missing following permissions to run this command: {missing}")

        elif isinstance(original, commands.MissingAnyRole):
            missing = self.__parse_missing(original.missing_roles, ", ")
            await ctx.send(f"Sorry, you need any of the following roles to run this command: {missing}")

        elif isinstance(original, commands.MissingRole):
            await ctx.send(f"Sorry, you are missing following role to run this command: `{original.missing_role}`")

        # Cog exceptions
        elif isinstance(original, commands.ExtensionAlreadyLoaded):
            await ctx.send(f"Extension `{original.name}` is already loaded. Please ensure the full "
                           f"extension name was given.")

        elif isinstance(original, commands.ExtensionNotFound):
            await ctx.send(f"Extension `{original.name}` could not be found. Please ensure the full "
                           f"extension name was given.")

        elif isinstance(original, commands.ExtensionNotLoaded):
            await ctx.send(f"Extension `{original.name}` is not loaded. Please ensure the full extension name was given.")

        # DeepL related errors. Rest of the expected exceptions should fall into this category
        elif isinstance(original, DeepLError):
            await ctx.send(str(original))

        # Unexpected exceptions fall here
        else:
            self.__log_unexpected_error(original)
            print()
            await ctx.send(f"Unexpected error: `{type(original).__name__}`. Contact the bot owner to resolve "
                           f"this issue.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandlerCog(bot))
