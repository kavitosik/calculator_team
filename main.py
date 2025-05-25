import asyncio
import os
import sqlite3
import sympy
import numpy as np
from datetime import datetime
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import find_dotenv, load_dotenv
from loguru import logger
from typing import Tuple, Optional

load_dotenv(find_dotenv())
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

# Создаем клавиатуру с примерами
examples_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="2 + 2 * 3"),
            KeyboardButton(text="x² - 5x + 6 = 0"),
        ],
        [
            KeyboardButton(text="√16 + ∛27"),
            KeyboardButton(text="sin(π/2) + cos(0)"),
        ],
        [
            KeyboardButton(text="∫(x^2, (x, 0, 3))"),
            KeyboardButton(text="derivative(x^3, x)"),
        ],
        [
            KeyboardButton(text="Отключить клавиатуру"),
            KeyboardButton(text="Помощь"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Введите математическую задачу..."
)

def save_query_to_db(user_id: int, username: str, query: str, result: str, solution: str):
    """Save user query to the database with detailed solution"""
    conn = sqlite3.connect("math_bot.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO query_history 
        (user_id, username, query, result, solution, timestamp) 
        VALUES (?, ?, ?, ?, ?, datetime('now'))""",
        (user_id, username, query, result, solution)
    )
    
    conn.commit()
    conn.close()

def get_user_history(user_id: int, limit: int = 10):
    """Get user query history"""
    conn = sqlite3.connect("math_bot.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT query, result, solution, timestamp 
        FROM query_history 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?""",
        (user_id, limit)
    )
    
    history = cursor.fetchall()
    conn.close()
    return history

def solve_math_problem(problem: str) -> Tuple[Optional[str], Optional[str]]:
    """Solve various math problems with detailed steps"""
    try:
        problem = problem.strip()
        
        # 1. Простые вычисления
        if all(c not in problem for c in ['=', '∫', 'derivative', 'lim']):
            x = sympy.symbols('x')
            expr = sympy.sympify(problem)
            steps = f"Вычисляем выражение:\n{expr} = "
            result = expr.evalf()
            steps += f"{result}\n\n"
            steps += f"Пошагово:\n{sympy.pretty(expr)} = {result}"
            return str(result), steps
        
        # 2. Решение уравнений
        if '=' in problem:
            x = sympy.symbols('x')
            equation = sympy.Eq(*map(sympy.sympify, problem.split('=')))
            solutions = sympy.solve(equation, x)
            
            steps = f"Решаем уравнение:\n{sympy.pretty(equation)}\n\n"
            steps += "Шаги решения:\n"
            for i, sol in enumerate(solutions, 1):
                steps += f"{i}. x = {sol}\n"
            
            return f"x = {solutions}", steps
        
        # 3. Производные
        if problem.startswith('derivative'):
            _, func, var = problem.split('(')[1].split(')')[0].split(',')
            x = sympy.symbols(var.strip())
            f = sympy.sympify(func.strip())
            derivative = sympy.diff(f, x)
            
            steps = f"Находим производную:\nd/d{var} ({func}) = "
            steps += f"\n{sympy.pretty(derivative)}\n\n"
            steps += "Пошаговое решение:\n"
            steps += sympy.pretty(sympy.Derivative(f, x)) + " = "
            steps += sympy.pretty(derivative)
            
            return str(derivative), steps
        
        # 4. Интегралы
        if problem.startswith('∫') or problem.startswith('integral'):
            parts = problem.split('(')[1].split(')')[0].split(',')
            func = parts[0].strip()
            var_info = parts[1].strip()[1:-1].split(',')
            var = var_info[0].strip()
            if len(var_info) > 1:
                lower = var_info[1].strip()
                upper = var_info[2].strip()
                x = sympy.symbols(var)
                f = sympy.sympify(func)
                integral = sympy.integrate(f, (x, lower, upper))
                
                steps = f"Вычисляем определённый интеграл:\n∫({func})d{var} от {lower} до {upper} = "
                steps += f"\n{sympy.pretty(integral)}\n\n"
                steps += "Пошаговое решение:\n"
                steps += sympy.pretty(sympy.Integral(f, (x, lower, upper))) + " = "
                steps += sympy.pretty(integral)
            else:
                x = sympy.symbols(var)
                f = sympy.sympify(func)
                integral = sympy.integrate(f, x)
                
                steps = f"Находим неопределённый интеграл:\n∫({func})d{var} = "
                steps += f"\n{sympy.pretty(integral)} + C\n\n"
                steps += "Пошаговое решение:\n"
                steps += sympy.pretty(sympy.Integral(f, x)) + " = "
                steps += sympy.pretty(integral) + " + C"
            
            return str(integral), steps
        
        # 5. Матрицы и системы уравнений
        if 'matrix' in problem.lower() or 'system' in problem.lower():
            # Реализация работы с матрицами
            pass
        
        return None, "Не удалось распознать тип задачи. Попробуйте сформулировать иначе."
    
    except Exception as e:
        logger.error(f"Math solving error: {e}")
        return None, f"Ошибка при решении: {str(e)}"

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    welcome_msg = (
        f"Привет, {html.bold(message.from_user.full_name)}! 👋\n\n"
        "Я - продвинутый математический бот 🧮\n"
        "Я могу решать различные математические задачи с подробными объяснениями:\n\n"
        "🔹 Арифметические выражения\n"
        "🔹 Алгебраические уравнения\n"
        "🔹 Дифференциальное исчисление\n"
        "🔹 Интегральное исчисление\n"
        "🔹 Тригонометрические выражения\n"
        "🔹 Матричные вычисления\n\n"
        "Примеры запросов:\n"
        "• 2 + 2 * 3\n"
        "• x^2 - 5x + 6 = 0\n"
        "• derivative(x^3, x)\n"
        "• ∫(x^2, (x, 0, 3))\n"
        "• matrix([[1, 2], [3, 4]]) * matrix([[5], [6]])\n\n"
        "Доступные команды:\n"
        "/history - история запросов\n"
        "/examples - примеры задач\n"
        "/help - справка по возможностям"
    )
    await message.answer(welcome_msg, reply_markup=examples_keyboard)

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = (
        "📚 Справка по использованию бота:\n\n"
        "1. <b>Базовые операции</b>:\n"
        "   +, -, *, /, ^ или ** - возведение в степень\n"
        "   sqrt(x) - квадратный корень\n\n"
        "2. <b>Уравнения</b>:\n"
        "   Формат: x^2 - 5x + 6 = 0\n\n"
        "3. <b>Производные</b>:\n"
        "   Формат: derivative(x^3, x)\n\n"
        "4. <b>Интегралы</b>:\n"
        "   Неопределённый: ∫(x^2, x)\n"
        "   Определённый: ∫(x^2, (x, 0, 3))\n\n"
        "5. <b>Тригонометрия</b>:\n"
        "   sin(x), cos(x), tan(x)\n"
        "   π (pi) - число пи\n\n"
        "6. <b>Матрицы</b>:\n"
        "   matrix([[1, 2], [3, 4]])\n\n"
        "Для примеров используйте /examples"
    )
    await message.answer(help_text)


@dp.message()
async def echo_handler(message: Message) -> None: 

@dp.message(F.text.lower() == "помощь")
async def help_handler(message: Message) -> None:
    await command_help_handler(message)

@dp.message()
async def handle_math_query(message: Message) -> None:
    if message.text.startswith('/'):
        return
        
    query = message.text
    result, solution = solve_math_problem(query)
    
    if result is None:
        await message.answer(solution)
        return
    
    # Сохраняем в базу данных
    save_query_to_db(
        user_id=message.from_user.id,
        username=message.from_user.username,
        query=query,
        result=result,
        solution=solution
    )
    
    # Отправляем ответ
    response = (
        f"🔹 <b>Задача</b>:\n{query}\n\n"
        f"🔸 <b>Результат</b>:\n{result}\n\n"
        f"📝 <b>Решение</b>:\n{solution}"
    )
    await message.answer(response)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Bot starting...")
    
    # Инициализация БД
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
                solution TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON query_history(user_id)")
        conn.commit()
        conn.close()
    
    asyncio.run(main())