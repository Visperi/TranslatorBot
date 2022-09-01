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
from discord.ext import commands


class ManagementCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="load")
    async def load_cog(self, ctx: discord.Message):
        raise NotImplementedError()

    @commands.command(name="unload")
    async def unload_cog(self, ctx: discord.Message):
        raise NotImplementedError()

    @commands.command(name="reload")
    async def reload_cog(self, ctx: discord.Message):
        raise NotImplementedError()

    async def get_translation_limits(self):
        raise NotImplementedError()

    @commands.command(name="sync")
    async def sync_commands(self, ctx: discord.Message, guild_id: int = None) -> None:
        await self.bot.tree.sync(guild=guild_id)
        await ctx.send("Commands synced!")


async def setup(bot: commands.Bot):
    await bot.add_cog(ManagementCog(bot))
