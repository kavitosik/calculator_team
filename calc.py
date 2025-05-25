import math
import ast

def safe_eval(expression: str):
    """Безопасное вычисление математических выражений"""
    # Разрешенные математические функции и константы
    allowed_names = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,  # Добавили натуральный логарифм
        'log10': math.log10,
        'ln': math.log,   # Альяс для натурального логарифма
        'pi': math.pi,
        'e': math.e,
        'exp': math.exp,
    }
    
    # Проверка на безопасность выражения
    try:
        for node in ast.walk(ast.parse(expression, mode='eval')):
            if isinstance(node, ast.Name) and node.id not in allowed_names:
                raise ValueError(f"Использование '{node.id}' не разрешено")
    except SyntaxError:
        raise ValueError("Некорректный синтаксис выражения")
    
    # Заменяем символы для удобства
    expression = expression.replace('√', 'sqrt').replace('π', 'pi')
    
    try:
        return eval(expression, {'__builtins__': {}}, allowed_names)
    except Exception as e:
        raise ValueError(f"Ошибка вычисления: {str(e)}")

def calculate_expression(expression: str) -> str:
    """Основная функция для вычисления выражений"""
    try:
        result = safe_eval(expression)
        return str(result)
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise ValueError(f"Неизвестная ошибка: {str(e)}")