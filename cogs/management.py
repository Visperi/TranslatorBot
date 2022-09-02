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
from cogs.commands import TranslationCog
from translator_bot import TranslatorBot


class ManagementCog(commands.Cog):

    def __init__(self, bot: TranslatorBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.group(name="extension")
    async def manage_extensions(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid extension management command: `{ctx.message.content.split()[1]}`")

    @manage_extensions.command(name="load")
    async def load_cog(self, ctx: commands.Context, extension_name: str):
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
    async def unload_cog(self, ctx: commands.Context, extension_name: str):
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
    async def reload_cog(self, ctx: commands.Context, extension_name: str):
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
        response = await TranslationCog.request_deepl_api(self.bot, TranslationCog.base_url + "/usage")
        d = json.loads(response)
        character_count = d["character_count"]
        character_limit = d["character_limit"]

        await ctx.send(f"Character count: {character_count}\n"
                       f"Character limit: {character_limit}\n\n"
                       f"Usage: {round(character_count / character_limit, 3)}%")

    @commands.command(name="sync")
    async def sync_commands(self, ctx: commands.Context, guild_id: int = None) -> None:
        await self.bot.tree.sync(guild=guild_id)
        await ctx.send("Commands synced!")

    @commands.command("getlangs")
    async def fetch_supported_languages(self, ctx: commands.Context):
        resp = await TranslationCog.request_deepl_api(self.bot, TranslationCog.base_url + "/languages?type=target")
        langs = json.loads(resp)
        print(langs)

        with open("supported_languages.json", "w") as languages_file:
            json.dump(langs, languages_file, indent=4, ensure_ascii=False)

        await ctx.send("Supported languages updated. Commands cog must be reloaded after this operation.")


async def setup(bot: TranslatorBot):
    await bot.add_cog(ManagementCog(bot))
