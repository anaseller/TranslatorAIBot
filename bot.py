from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import requests
import asyncio
import logging
from datetime import date
from database import get_limit_data, set_limit_data

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DAILY_LIMIT = 1500
LANGUAGES = {
    'ru': 'Русский',
    'pt': 'Português',
    'fr': 'Français',
    'en': 'English'
}

# Logging setup for debugging
logging.basicConfig(level=logging.INFO)

# Using a dictionary to store message data in order to preserve state
message_data_store = {}


def check_and_reset_limit():
    today = date.today().isoformat()
    saved_date, count = get_limit_data()
    if saved_date != today:
        set_limit_data(today, 0)
        return 0
    return count


def increment_limit():
    today = date.today().isoformat()
    saved_date, count = get_limit_data()
    count += 1
    set_limit_data(today, count)
    return count


async def translate_text_gemini(text: str, target_lang: str) -> str:
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'key': GEMINI_API_KEY
    }

    # Prompt for translation
    prompt = f'Translate this text to {LANGUAGES[target_lang]} exactly, return ONLY the translated text, no additional words or explanations:\n\n"{text}"'

    # Request structure for Gemini 1.5 Flash
    json_data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,  # translation accuracy
            "maxOutputTokens": 512  # Maximum number of tokens in the response
        }
    }

    try:
        response = requests.post(url, headers=headers, params=params, json=json_data)
        response.raise_for_status()  # Raises an exception for HTTP errors (4xx or 5xx)

        resp_json = response.json()

        # Response parsing for Gemini 1.5 Flash
        if 'candidates' in resp_json and resp_json['candidates']:
            # The response is located in content.parts[0].text
            for candidate in resp_json['candidates']:
                if 'content' in candidate and 'parts' in candidate['content'] and candidate['content']['parts']:
                    return candidate['content']['parts'][0]['text'].strip()
            logging.warning(f"Gemini API returned no usable content in candidates: {resp_json}")
            return '[Error: No translation candidates found in Gemini response]'
        else:
            logging.warning(f"Gemini API returned no candidates for translation: {resp_json}")
            return '[Error: No translation candidates from Gemini API]'
    except requests.exceptions.RequestException as e:
        # Logging the full response for debugging
        logging.error(f"Error calling Gemini API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Gemini API full error response: {e.response.text}")
        return f'[Error in translation API: {e}]'
    except Exception as e:
        logging.error(f"Unexpected exception during Gemini translation: {e}")
        return f'[Exception: {e}]'


@dp.message()
async def handle_message(message: types.Message):
    count = check_and_reset_limit()
    if count >= DAILY_LIMIT:
        await message.reply("Daily translation limit reached. The bot is ‘sleeping’ until tomorrow.")
        return

    original_text = message.text
    if not original_text:
        return

    increment_limit()

    # Creating buttons for language selection
    buttons = []
    for code, name in LANGUAGES.items():
        flag = {'ru': '🇷🇺', 'pt': '🇧🇷', 'fr': '🇫🇷', 'en': '🇬🇧'}.get(code, '')
        buttons.append(InlineKeyboardButton(text=f'{flag} {name}', callback_data=f'translate_{code}'))

    # Create a keyboard by passing buttons as a list of lists (each inner list is a row)
    # Use list comprehension to distribute buttons across rows
    keyboard_rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    sent = await message.answer(
        '💬 Translation available:\nSelect a language:',
        reply_markup=keyboard
    )
    # Save the original text, associating it with the bot message ID
    message_data_store[(sent.chat.id, sent.message_id)] = {
        'original_text': original_text
    }


@dp.callback_query(lambda c: c.data and c.data.startswith('translate_'))
async def process_translate(callback: types.CallbackQuery):
    target_lang = callback.data.split('_')[1]
    key = (callback.message.chat.id, callback.message.message_id)

    # Retrieve the original text from storage
    data = message_data_store.get(key)
    if not data:
        await callback.answer("Original message not found or has expired.", show_alert=True)
        return

    original_text = data['original_text']

    # Send a temporary message while the translation is in progress
    await callback.answer("Translating…", show_alert=False)  # You can remove show_alert=False if you don't want the notification

    translation = await translate_text_gemini(original_text, target_lang)

    text = f'{LANGUAGES[target_lang]} Translation: {translation}\n\n🔁 Show in another language:'

    # Create new buttons for selecting a different language
    buttons = []
    for code, name in LANGUAGES.items():
        if code != target_lang:  # Exclude the current language from the buttons
            flag = {'ru': '🇷🇺', 'pt': '🇧🇷', 'fr': '🇫🇷', 'en': '🇬🇧'}.get(code, '')
            buttons.append(InlineKeyboardButton(text=f'{flag} {name}', callback_data=f'translate_{code}'))

    # Create a keyboard with buttons for other languages
    keyboard_rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    # Edit the original bot message
    await callback.message.edit_text(text, reply_markup=keyboard)
    # Send confirmation that the request has been processed (so the button stops "spinning")
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())