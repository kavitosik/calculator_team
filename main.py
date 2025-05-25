import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from dotenv import find_dotenv, load_dotenv
from loguru import logger

load_dotenv(find_dotenv)
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

# Database functions
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
        f"Hello, {html.bold(message.from_user.full_name)}!\n\n"
        "I'm a math bot. Send me math expressions to evaluate.\n"
        "Use /history to see your last queries."
    )
    await message.answer(welcome_msg)

@dp.message(Command("history"))
async def command_history_handler(message: Message) -> None:
    """Handler for /history command"""
    user_id = message.from_user.id
    history = get_user_history(user_id)
    
    if not history:
        await message.answer("Your query history is empty.")
        return
    
    history_text = "📚 Your last queries:\n\n"
    for idx, (query, result, timestamp) in enumerate(history, 1):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d.%m %H:%M")
        history_text += f"{idx}. {timestamp}\n🔹 {query}\n"
        if result:
            history_text += f"🔸 Result: {result}\n"
        history_text += "\n"
       
    await message.answer(history_text)

@dp.message()
async def handle_math_query(message: Message) -> None:
    """Handle math queries"""
    try:
        # Try to evaluate the math expression
        query = message.text.strip()
        result = str(eval(query))
        
        # Save to database
        save_query_to_db(
            user_id=message.from_user.id,
            username=message.from_user.username,
            query=query,
            result=result
        )
        
        # Send response
        response = f"🔹 {query}\n= {html.bold(result)}"
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error processing math query: {e}")
        await message.answer("Please send a valid math expression.")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Bot starting...")
    
    # Ensure database exists
    if not os.path.exists("math_bot.db"):
        logger.info("Creating database...")
        import create_db
        create_db.create_database()
    
    asyncio.run(main())
