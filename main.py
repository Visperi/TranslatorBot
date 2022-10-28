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
from translator_bot import TranslatorBot
from typing import Union, Iterable

BOT_VERSION = "0.7"
COMMAND_PREFIX: Union[str, Iterable[str]] = "?"


def start():
    with open("credentials.json", "r") as credential_file:
        credentials = json.load(credential_file)

    discord_api_token = credentials["api_tokens"]["discord"]
    deepl_api_token = credentials["api_tokens"]["deepl"]
    bot = TranslatorBot(deepl_api_token, COMMAND_PREFIX)

    bot.run(discord_api_token, reconnect=True)


if __name__ == '__main__':
    start()
