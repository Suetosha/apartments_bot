from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dotenv import load_dotenv

from database.activity import get_liked_apartments
from database.filter import get_user_filters
from database.users import save_user
from keyboards.favorites_kb import favorites_kb

load_dotenv()
router = Router()


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_user(user_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Найти квартиру", callback_data="start_filter")],
        [InlineKeyboardButton(text="Сдать квартиру", callback_data="list_an_apartment")]
    ])

    sent_message = await message.answer(
        'Здравствуйте!\n'
        'Вас приветствует бот для поиска и сдачи квартир.\n'
        'Что вас интересует?',
        reply_markup=keyboard
    )
    await state.update_data(message_id=sent_message.message_id)



@router.message(Command("view_apartments"))
async def view_apartments_command(message: Message):
    # Отправляем сообщение с кнопкой, которая вызывает callback_query
    button = types.InlineKeyboardButton(text="Начать просмотр", callback_data="view_apartments")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Отправляем сообщение с кнопкой
    await message.answer("Нажмите кнопку для просмотра квартир:", reply_markup=keyboard)




@router.message(Command("filter"))
async def filter_command(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Отправляем сообщение с кнопкой, которая вызывает callback_query
    button = types.InlineKeyboardButton(text="Редактировать фильтр", callback_data="start_filter")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])

    filter_data = get_user_filters(user_id)

    if filter_data:
        result_text = (
            f"🔹 Город: {filter_data['city']}\n"
            f"🔹 Метры: {filter_data['meters']}"
        )
        # Отправляем сообщение с кнопкой
        sent_message = await message.answer(f"Ваш фильтр:\n{result_text}", reply_markup=keyboard)
    else:
        sent_message = await message.answer('Фильтр ещё не создан.', reply_markup=keyboard)

    await state.update_data(message_id=sent_message.message_id)


@router.message(Command('favorites'))
async def favorites_command(message: Message):
    user_id = message.from_user.id
    liked_apartments = get_liked_apartments(user_id)

    # Отправляем сообщение с временной клавиатурой и получаем его объект
    sent_message = await message.answer('Список избранных квартир')

    # Теперь у нас есть message_id
    message_id = sent_message.message_id

    # Создаем клавиатуру с учетом полученного message_id
    keyboard = favorites_kb(liked_apartments, user_id, message_id=message_id)

    # Редактируем сообщение, добавляя клавиатуру
    await sent_message.edit_text('Список избранных квартир', reply_markup=keyboard)


@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.delete()





