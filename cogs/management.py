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
        await self.bot.load_extension(extension_name)
        await ctx.send(f"Successfully loaded extension `{extension_name}`.")

    @manage_extensions.command(name="unload")
    async def unload_cog(self, ctx: commands.Context, extension_name: str) -> None:
        """
        Unload an extension atomically.

        :param ctx:
        :param extension_name: Extension name to unload.
        """
        await self.bot.unload_extension(extension_name)
        await ctx.send(f"Successfully unloaded extension `{extension_name}`.")

    @manage_extensions.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, extension_name: str) -> None:
        """
        Reload an extension atomically.

        :param ctx:
        :param extension_name: Extension name to reload.
        """
        await self.bot.reload_extension(extension_name)
        await ctx.send(f"Successfully reloaded extension `{extension_name}`")

    @commands.command(name="usage")
    async def get_deepl_translation_limits(self, ctx: commands.Context) -> None:
        """
        Get DeepL API usage status for the bot.

        :param ctx:
        """
        response = await self.bot.deepl_client.get_usage()
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
        Update supported languages.

        :param ctx:
        """
        current_languages = self.bot.deepl_client.supported_languages
        updated_languages = await self.bot.deepl_client.update_supported_languages()

        diff = len(updated_languages) - len(current_languages)
        message = "Supported languages updated. "
        if diff == 0:
            message += "There were no new languages."
        else:
            message += f" There were {diff} new languages."

        await ctx.send(message)


async def setup(bot: TranslatorBot):
    await bot.add_cog(ManagementCog(bot))
