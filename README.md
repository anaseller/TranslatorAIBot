# Translator AI Bot 

This is a Python-based Telegram bot. It uses Gemini AI to improve translation quality and contextual accuracy.
The bot translates every message in the chat, offering the user a choice of translation into four languages.
Translation between different languages happens within a single message by editing the bot’s original message.

## ✨ Features

- Automatic translation of every chat message using Gemini AI for contextual accuracy
- Inline translation buttons embedded under each message (e.g., "Show in English", "Show in German", etc.)
- Translations appear in the same message via inline edits
- Supports four target languages (fully customizable)
- Lightweight, privacy-conscious design – no message storage or logging
- Clean integration with group chats, non-intrusive UX

## 🚀 Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/anaseller/TranslatorAIBot.git
   cd TranslatorAIBot
   ```

2. Set up your virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:

   ```
   TELEGRAM_TOKEN=your_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. Run the bot:

   ```bash
   python bot.py
   ```
   

## 🛠️ Structure

```
TranslatorAIBot/
├── bot.py               # Main bot logic
├── database.py          # (Optional) Storage logic
├── requirements.txt     # Python dependencies
├── .env                 # Secret credentials (excluded from Git)
├── .gitignore
└── limit_data.txt       # Rate-limit or config file
```


## 📜 License

MIT License
