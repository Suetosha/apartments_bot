from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from dotenv import load_dotenv
from lexicon.lexicon import LEXICON
from database.activity import get_liked_apartments
from database.apartments import get_apartments_by_landlord
from database.filter import get_user_filters
from database.users import save_user
from keyboards.tenant_kb import favorites_kb
from keyboards.landlord_kb import landlord_apartments_kb
from utils.fsm import FSMFillForm

load_dotenv()
router = Router()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username

    save_user(user_id, username)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Найти квартиру", callback_data="start_filter")],
        [InlineKeyboardButton(text="Сдать квартиру", callback_data="list_an_apartment")]
    ])

    sent_message = await message.answer(LEXICON['start'], reply_markup=keyboard)
    await state.update_data(message_id=sent_message.message_id)


@router.message(Command("view_apartments"))
async def view_apartments_command(message: Message, state: FSMContext):
    await state.clear()
    # Отправляем сообщение с кнопкой, которая вызывает callback_query
    button = types.InlineKeyboardButton(text=LEXICON['start_view'], callback_data="view_apartments")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])

    # Отправляем сообщение с кнопкой
    await message.answer(LEXICON['press_for_view'], reply_markup=keyboard)


@router.message(Command("filter"))
async def filter_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    # Отправляем сообщение с кнопкой, которая вызывает callback_query
    button = types.InlineKeyboardButton(text=LEXICON['edit_filter'], callback_data="start_filter")
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
        sent_message = await message.answer(LEXICON['filter_not_created'], reply_markup=keyboard)

    await state.update_data(message_id=sent_message.message_id)


@router.message(Command('favorites'))
async def favorites_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    liked_apartments = get_liked_apartments(user_id)

    # Отправляем сообщение с временной клавиатурой и получаем его объект
    sent_message = await message.answer(LEXICON['favorite_list'])

    # Теперь у нас есть message_id
    message_id = sent_message.message_id

    # Создаем клавиатуру с учетом полученного message_id
    keyboard = favorites_kb(liked_apartments, user_id, message_id=message_id)

    # Редактируем сообщение, добавляя клавиатуру
    await sent_message.edit_text(LEXICON['favorite_list'], reply_markup=keyboard)


@router.message(Command('publish_apartment'))
async def publish_apartment_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=LEXICON['choose_city_landlord'])
    await state.set_state(FSMFillForm.city)


@router.message(Command('view_published_apartments'))
async def view_published_apartments_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    apartments = get_apartments_by_landlord(user_id)

    # Отправляем сообщение с временной клавиатурой и получаем его объект
    sent_message = await message.answer(LEXICON['published_list'])

    message_id = sent_message.message_id

    keyboard = landlord_apartments_kb(apartments, message_id)
    await sent_message.edit_text(LEXICON['published_list'], reply_markup=keyboard)


