import aiosqlite
import table
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = table.quiz_data[current_question_index]['correct_option']
    opts = table.quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{table.quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_result(user_id, 0)
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(table.DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
async def get_quiz_result(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(table.DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT result FROM quiz_results WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
            
async def get_quiz_results():
     # Подключаемся к базе данных
     async with aiosqlite.connect(table.DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT user_id, last_result FROM quiz_results ORDER BY last_result DESC') as cursor:
            # Возвращаем результат
            rows = await cursor.fetchall()
            results = [list(row) for row in rows]
            if results is not None:
                return results
            else:
                return 0

async def update_quiz_index(u_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(table.DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (u_id, index))
        # Сохраняем изменения
        await db.commit()

async def update_quiz_result(u_id, result):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(table.DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        params = (u_id, result)
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, result) VALUES (?, ?)', params)
        # Сохраняем изменения
        await db.commit()

async def update_last_result(u_id, current_result):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(table.DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        params = (u_id, current_result)
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, last_result) VALUES (?, ?)', params)
        await db.commit()

async def print_results():
    result = await get_quiz_results()
    string = ""
    for x in result:
        string += str(x[0]) + ": " + str(x[1]) + " очков\n"
    return string




