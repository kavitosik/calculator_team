1. что такое Inline-клавиатура?

Inline-клавиатура в библиотеке Aiogram — это клавиатура, кнопки которой связаны не с областью клавиатуры в мессенджере, а с сообщением в чате. При этом пользователь видит не только inline-кнопки, но и основную клавиатуру. 





2. Создание inline клавиатуры




Для создания inline-клавиатуры в Aiogram используются следующие классы:

InlineKeyboardMarkup — создаёт разметку клавиатуры, определяет, как будут располагаться кнопки.
InlineKeyboardButton — представляет отдельную кнопку, позволяет задавать её текст и действие при нажатии.

Пример кода, который создаёт две inline-кнопки:

```python
from aiogram import types  
  
# Создаём клавиатуру:
keyboard = types.InlineKeyboardMarkup(row_width=2)  
# Создаём кнопки:
button1 = types.InlineKeyboardButton(text="Кнопка 1", callback_data="button1")  
button2 = types.InlineKeyboardButton(text="Кнопка 2", callback_data="button2")  
# Добавляем кнопки на клавиатуру:
keyboard.add(button1, button2)  
# Отправляем сообщение с клавиатурой: 
await bot.send_message(chat_id=chat_id, text="Выберите кнопку:", reply_markup=keyboard)  
```

В этом примере клавиатура с двумя кнопками добавляется с помощью метода add() класса InlineKeyboardMarkup. Каждая кнопка создаётся с помощью класса InlineKeyboardButton, у которого есть два обязательных параметра: text — текст кнопки, и callback_data — данные, которые будут отправлены боту при нажатии на кнопку

Видео-инструкция по созданию inline клавиатуры в Aiogram:

https://ya.ru/search/?text=inline+%D0%BA%D0%BB%D0%B0%D0%B2%D0%B8%D0%B0%D1%82%D1%83%D1%80%D0%B0+aiogram&lr=20728&search_source=yaru_desktop_common&search_domain=yaru




3. Обработка нажатий на кнопки

Для обработки нажатий на inline-кнопки в Aiogram используется метод callback_query_handler() и регистрация его в диспетчере бота. Пример кода, который обрабатывает нажатия на кнопки:

```python
from aiogram import Dispatcher, types  
  
async def button_callback(callback_query: types.CallbackQuery):  
    # Получаем данные кнопки  
    data = callback_query.data  
    # Проверяем, какая кнопка была нажата  
    if data == "button1":  
        await bot.answer_callback_query(callback_query_id=callback_query.id, text="Вы нажали кнопку 1")  
    elif data == "button2":  
        await bot.answer_callback_query(callback_query_id=callback_query.id, text="Вы нажали кнопку 2")  
    # Регистрируем обработчик нажатий на кнопки  
    dp = Dispatcher(bot)  
    dp.register_callback_query_handler(button_callback)  
```

В этом примере функция button_callback получает в качестве параметра объект CallbackQuery, содержащий информацию о нажатой кнопке. Она проверяет значение параметра data объекта CallbackQuery, чтобы определить, какая кнопка была нажата, и отправляет соответствующее сообщение пользователю с помощью метода answer_callback_query(). 