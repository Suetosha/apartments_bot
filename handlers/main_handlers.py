from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.landlord_kb import published_apartments_kb
from keyboards.main_menu import options_menu_kb
from lexicon.lexicon import LEXICON, get_result_text

from database.activity import get_liked_apartments
from database.apartments import get_apartments_by_landlord
from database.filter import get_user_filters
from database.users import save_user

from keyboards.tenant_kb import favorites_kb, start_view_kb, edit_filter_kb

from utils.fsm import FSMFillForm

router = Router()


# Команда /start.
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username
    save_user(user_id, username)

    keyboard = await options_menu_kb()
    sent_message = await message.answer(LEXICON['start'], reply_markup=keyboard)
    await state.update_data(message_id=sent_message.message_id)


# Команда /view_apartments. Просмотр квартир по фильтру
@router.message(Command("view_apartments"))
async def view_apartments_command(message: Message, state: FSMContext):
    await state.clear()

    keyboard = await start_view_kb()
    await message.answer(LEXICON['press_for_view'], reply_markup=keyboard)


# Команда /filter. Создание нового фильтра для поиска квартир
@router.message(Command("filter"))
async def filter_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    keyboard = await edit_filter_kb()

    filter_data = get_user_filters(user_id)

    if filter_data:
        result_text = get_result_text(filter_data['city'], filter_data['meters'])
        sent_message = await message.answer(f"Ваш фильтр:\n{result_text}", reply_markup=keyboard)
    else:
        sent_message = await message.answer(LEXICON['filter_not_created'], reply_markup=keyboard)

    await state.update_data(message_id=sent_message.message_id)


# Команда /favorites. Получение избранных квартир
@router.message(Command('favorites'))
async def favorites_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    liked_apartments = get_liked_apartments(user_id)

    sent_message = await message.answer(LEXICON['favorite_list'])
    message_id = sent_message.message_id

    keyboard = await favorites_kb(liked_apartments, user_id, message_id=message_id)

    await sent_message.edit_text(LEXICON['favorite_list'], reply_markup=keyboard)


# Команда /publish_apartment. Начало заполнения формы на создание квартиры
@router.message(Command('publish_apartment'))
async def publish_apartment_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=LEXICON['choose_city_landlord'])
    await state.set_state(FSMFillForm.city)


# Команда /view_published_apartments. Просмотр опубликованных пользователем квартир
@router.message(Command('view_published_apartments'))
async def view_published_apartments_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    apartments = get_apartments_by_landlord(user_id)

    sent_message = await message.answer(LEXICON['published_list'])
    message_id = sent_message.message_id

    keyboard = published_apartments_kb(apartments, message_id)
    await sent_message.edit_text(LEXICON['published_list'], reply_markup=keyboard)
