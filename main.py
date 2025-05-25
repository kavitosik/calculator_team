import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (Message, ReplyKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardRemove)

from dotenv import find_dotenv, load_dotenv
from loguru import logger

from calc import calculate_expression

load_dotenv(find_dotenv())
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


examples_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="2 + 2"),
            KeyboardButton(text="10 * 5"),
        ],
        [
            KeyboardButton(text="√16"),
            KeyboardButton(text="3 ** 3"),
        ],
        [
            KeyboardButton(text="π"),
            KeyboardButton(text="math.sin(0.5)"),
        ],
        [
            KeyboardButton(text="Отключить клавиатуру"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пример или введите свой..."
)


def save_query_to_db(user_id: int, username: str, query: str, result: str = None):
    """Save user query to the database"""
    conn = sqlite3.connect("math_bot.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO query_history (user_id, username, query, result) VALUES (?, ?, ?, ?)",
        (user_id, username, query, result)
    )

    conn.commit()
    conn.close()


def get_user_history(user_id: int, limit: int = 10):
    """Get user query history"""
    conn = sqlite3.connect("math_bot.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT query, result, timestamp FROM query_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )

    history = cursor.fetchall()
    conn.close()
    return history


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Handler for /start command"""
    welcome_msg = (
        f"Привет, {html.bold(message.from_user.full_name)}! 👋\n\n"
        "Я - математический бот-калькулятор 🧮\n"
        "Отправь мне математическое выражение, и я вычислю его.\n\n"
        "Примеры использования:\n"
        "• 2 + 2 * 3\n"
        "• √16 (или sqrt(16))\n"
        "• math.sin(math.pi/2)\n"
        "• 2**10\n\n"
        "Доступные команды:\n"
        "/history - история ваших запросов\n"
        "/examples - примеры выражений"
    )
    await message.answer(welcome_msg, reply_markup=examples_keyboard)


@dp.message(Command("history"))
async def command_history_handler(message: Message) -> None:
    """Handler for /history command"""
    user_id = message.from_user.id
    history = get_user_history(user_id)

    if not history:
        await message.answer("Ваша история запросов пуста.")
        return

    history_text = "📚 Ваши последние запросы:\n\n"
    for idx, (query, result, timestamp) in enumerate(history, 1):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d.%m %H:%M")
        history_text += f"{idx}. {timestamp}\n🔹 {query}\n"
        if result:
            history_text += f"🔸 Результат: {result}\n"
        history_text += "\n"

    await message.answer(history_text)


@dp.message(Command("examples"))
async def command_examples_handler(message: Message) -> None:
    """Show examples keyboard"""
    await message.answer(
        "Выберите пример или введите свое выражение:",
        reply_markup=examples_keyboard
    )


@dp.message(F.text.lower() == "отключить клавиатуру")
async def remove_keyboard_handler(message: Message) -> None:
    """Remove reply keyboard"""
    await message.answer(
        "Клавиатура отключена. Используйте /examples чтобы вернуть её.",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message()
async def handle_math_query(message: Message) -> None:
    """Handle math queries"""
    try:
        query = message.text.strip()
        result = calculate_expression(query)

        save_query_to_db(
            user_id=message.from_user.id,
            username=message.from_user.username,
            query=message.text,
            result=result
        )

        response = f"🔹 {message.text}\n= {html.bold(result)}"
        await message.answer(response)

    except ValueError as e:
        await message.answer(f"Ошибка: {e}\nПожалуйста, используйте только математические выражения.")
    except SyntaxError:
        await message.answer("Синтаксическая ошибка в выражении. Проверьте правильность ввода.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при вычислении: {e}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Bot starting...")

    if not os.path.exists("math_bot.db"):
        logger.info("Creating database...")
        conn = sqlite3.connect("math_bot.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                query TEXT NOT NULL,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    asyncio.run(main())
