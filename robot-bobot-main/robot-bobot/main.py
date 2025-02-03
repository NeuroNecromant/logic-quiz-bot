
import nest_asyncio
nest_asyncio.apply()
import aiosqlite
import asyncio
import logging
import table 
import quiz
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher()



@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
   
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await quiz.get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_result = await quiz.get_quiz_result(callback.from_user.id)

    current_result += 1
    current_question_index += 1
    await quiz.update_quiz_index(callback.from_user.id, current_question_index)
    await quiz.update_quiz_result(callback.from_user.id, current_result)

    if current_question_index < len(table.quiz_data):
        await quiz.get_question(callback.message, callback.from_user.id)
    else:
        await quiz.update_last_result(callback.from_user.id, current_result)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await quiz.get_quiz_index(callback.from_user.id)
    correct_option = table.quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {table.quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    
    current_question_index += 1
    await quiz.update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(table.quiz_data):
        await quiz.get_question(callback.message, callback.from_user.id)
    else:
        await quiz.update_last_result(callback.from_user.id, quiz.get_quiz_result())
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await quiz.new_quiz(message)

@dp.message(F.text == "Вывести рейтинг")
@dp.message(Command("rate"))
async def cmd_rate(message: types.Message):
    rating = await quiz.print_results()
    await message.answer(rating)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Вывести рейтинг"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True)) 



# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await table.create_table(dp.message)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
