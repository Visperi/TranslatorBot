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
from typing import Union, Iterable, Optional
import deepl
import logging
import discord
import aiohttp
import os


_logger = logging.getLogger(__name__)


class CommandPrefixParser:

    def __init__(self, command_prefix: Union[str, Iterable[str]]):
        self.command_prefix = command_prefix

    def __call__(self, *args, **kwargs):
        return self.command_prefix


class TranslatorBot(commands.Bot):

    def __init__(self, deepl_api_token: str, command_prefix: Union[str, Iterable[str]]):
        intents = discord.Intents.default()
        intents.message_content = True
        prefix_parser = CommandPrefixParser(command_prefix)
        self._aiohttp_session: Optional[aiohttp.ClientSession] = None
        self._deepl_client: Optional[deepl.Client] = None
        self._deepl_api_token: str = deepl_api_token
        self.cogs_path: str = f"{os.path.dirname(__file__)}/cogs"
        super().__init__(command_prefix=prefix_parser, intents=intents, case_insensitive=True)

    async def setup_hook(self):
        await self.__load_cogs()
        self._aiohttp_session = aiohttp.ClientSession(loop=self.loop, raise_for_status=True)
        self._deepl_client = deepl.Client(self._deepl_api_token, str(self.user), self.aiohttp_session)
        supported_languages = await self.deepl_client.update_supported_languages()
        _logger.info(f"Loaded {len(supported_languages)} supported languages.")

    @property
    def aiohttp_session(self):
        return self._aiohttp_session

    @property
    def deepl_client(self):
        return self._deepl_client

    # noinspection PyBroadException
    async def __load_cogs(self):
        startup_extensions = [f"cogs.{fname.rstrip('.py')}" for fname in os.listdir(self.cogs_path)
                              if fname.endswith(".py")]
        for extension in startup_extensions:
            try:
                await self.load_extension(extension)
            except:
                _logger.exception(f"Failed to load extension {extension}")

    async def fetch_url(self, url: str, timeout: int = 10, **kwargs) -> str:
        if not url:
            raise ValueError("Url must be provided.")
        async with self.aiohttp_session.get(url, timeout=timeout, **kwargs) as response:
            return await response.text()
