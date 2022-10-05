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


class ManagementCog(commands.Cog, name="Management",
                    description="Various bot owner only commands for managing the bot through Discord chat."):
    """
    A cog encapsulating various commands for managing the bot and DeepL data.
    """

    def __init__(self, bot: TranslatorBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.group(name="extension")
    async def manage_extensions(self, ctx: commands.Context) -> None:
        """
        Load, reload or unload an extension.
        :param ctx:
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid extension management command: `{ctx.message.content.split()[1]}`")

    @manage_extensions.command(name="load")
    async def load_cog(self, ctx: commands.Context, extension_name: str) -> None:
        """
        Load an extension atomically.
        :param ctx:
        :param extension_name: Extension name to load.
        """
        try:
            await self.bot.load_extension(extension_name)
            await ctx.send(f"Successfully loaded extension `{extension_name}`.")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"Extension `{extension_name}` is already loaded. Please ensure the full "
                           f"extension name was given.")
        except commands.ExtensionNotFound:
            await ctx.send(f"Extension `{extension_name}` could not be found. Please ensure the full "
                           f"extension name was given.")

    @manage_extensions.command(name="unload")
    async def unload_cog(self, ctx: commands.Context, extension_name: str) -> None:
        """
        Unload an extension atomically.
        :param ctx:
        :param extension_name: Extension name to unload.
        """
        try:
            await self.bot.unload_extension(extension_name)
            await ctx.send(f"Successfully unloaded extension `{extension_name}`.")
        except commands.ExtensionNotFound:
            await ctx.send(f"Extension `{extension_name}` could not be found. Please ensure the full "
                           f"extension name was given.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"Extension `{extension_name}` is not loaded. Please ensure the full "
                           f"extension name was given.")

    @manage_extensions.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, extension_name: str) -> None:
        """
        Reload an extension atomically.
        :param ctx:
        :param extension_name: Extension name to reload.
        """
        try:
            await self.bot.reload_extension(extension_name)
            await ctx.send(f"Successfully reloaded extension `{extension_name}`")
        except commands.ExtensionNotFound:
            await ctx.send(f"Extension `{extension_name}` could not be found. Please ensure the full "
                           f"extension name was given.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"Extension `{extension_name}` is not loaded. Please ensure the full "
                           f"extension name was given.")

    @commands.command(name="usage")
    async def get_deepl_translation_limits(self, ctx: commands.Context) -> None:
        """
        Get DeepL API usage status for the bot.
        :param ctx:
        """
        response = await self.bot.deepl.get_usage()
        character_count = response["character_count"]
        character_limit = response["character_limit"]

        await ctx.send(f"Character count: {character_count}\n"
                       f"Character limit: {character_limit}\n\n"
                       f"Usage: {round(character_count / character_limit, 3)}%")

    @commands.command(name="sync")
    async def sync_commands(self, ctx: commands.Context, guild_id: int = None) -> None:
        """
        Synchronize slash commands to Discord API for the bot. Bot owner command.
        :param ctx:
        :param guild_id: Guild ID to sync the commands for. If not provided, sync for all guilds.
        """
        await self.bot.tree.sync(guild=guild_id)
        await ctx.send("Commands synced!")

    @commands.command("getlangs")
    async def update_supported_languages(self, ctx: commands.Context) -> None:
        """
        Update supported languages in the supported_languages.json file.
        :param ctx:
        """
        langs = await self.bot.deepl.fetch_supported_languages()
        jsonified = [language.as_dict() for language in langs]

        with open("supported_languages.json", "w") as languages_file:
            json.dump(jsonified, languages_file, indent=4, ensure_ascii=False)

        await ctx.send("Supported languages updated. Commands cog must be reloaded after this operation.")


async def setup(bot: TranslatorBot):
    await bot.add_cog(ManagementCog(bot))
