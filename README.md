# TranslatorBot
A bot for translating Discord messages utilizing DeepL software. Both slash commands and message commands are supported.

Requirements:
- Python 3.8+
- discord.py 2.0.1
- aiohttp 3.8.1

Credentials file must exist in the project root directory. It must contain Discord API and DeepL API tokens in following format:

```json
{
    "api_tokens": {
        "deepl": "DeepL API token here",
        "discord": "Discord API token"
    }
}
```

# License
MIT License

Full license: [LICENSE](LICENSE)
