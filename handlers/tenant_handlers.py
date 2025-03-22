from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton

from dotenv import load_dotenv

from database.activity import mark_as_liked, mark_as_viewed, mark_as_unliked, get_liked_apartments
from database.apartments import get_apartments_by_filter, get_apartment
from keyboards.apartments_kb import get_feedback_keyboard
from keyboards.favorites_kb import favorite_apartment_selection_kb, favorites_kb
from utils.callback_factories import GetApartmentCallbackFactory, DeleteFavoriteCallbackFactory
from utils.fsm import FSMFillFilter

from database.filter import save_filter, get_user_filters

load_dotenv()
router = Router()



# Хэндлер для старта заполнения формы
@router.callback_query(lambda c: c.data == "start_filter")
async def start_fill_form(callback_query: CallbackQuery, state: FSMContext):
    # Получаем ID ранее отправленного сообщения
    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")

    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="Москва", callback_data="Москва")],
        [InlineKeyboardButton(text="Санкт-Петербург", callback_data="Санкт-Петербург")],
        [InlineKeyboardButton(text="Нижний Новгород", callback_data="Нижний Новгород")]
    ])

    sent_message = await callback_query.message.bot.edit_message_text(
        text="В каком городе ты ищешь квартиру?",
        message_id=sent_message_id,
        chat_id=callback_query.message.chat.id,
        reply_markup=keyboard,
    )

    await state.update_data(message_id=sent_message.message_id)
    await state.set_state(FSMFillFilter.city)


# Хэндлер для получения города
@router.callback_query(StateFilter(FSMFillFilter.city))
async def process_city(callback_query: CallbackQuery, state: FSMContext):
    city = callback_query.data  # Используем data из callback_query

    # Сохраняем город в данные состояния
    await state.update_data(city=city)

    # Получаем ID ранее отправленного сообщения
    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")

    # Создаём клавиатуру с вариантами метража
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="20 - 40 м²", callback_data="20 - 40 м²")],
            [InlineKeyboardButton(text="40 - 60 м²", callback_data="40 - 60 м²")],
            [InlineKeyboardButton(text="60 - 80 м²", callback_data="60 - 80 м²")],
            [InlineKeyboardButton(text="80 - 100 м²", callback_data="80 - 100 м²")],
            [InlineKeyboardButton(text="100 - и более м²", callback_data="100 - и более м²")]
        ],
        resize_keyboard=True
    )

    sent_message = await callback_query.message.bot.edit_message_text(
        "Какой метраж тебе нужен?",
        message_id=sent_message_id,
        chat_id=callback_query.message.chat.id,
        reply_markup=keyboard
    )

    # Переход к следующему состоянию
    await state.update_data(message_id=sent_message.message_id)
    await state.set_state(FSMFillFilter.meters)


# Хэндлер для получения метража
@router.callback_query(StateFilter(FSMFillFilter.meters))
async def process_meters(callback_query: CallbackQuery, state: FSMContext):

    # Получаем ID ранее отправленного сообщения
    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")

    meters = callback_query.data

    # Получаем данные из состояния
    data = await state.get_data()

    # Обновляем данные в состоянии
    await state.update_data(meters=meters)

    # Формируем сообщение с результатами
    result_text = (
        f"🔹 Город: {data.get('city')}\n"
        f"🔹 Метры: {meters}"
    )

    user_id = callback_query.from_user.id
    save_filter(user_id, data.get('city'), meters)

    # Создаем кнопку для начала просмотра квартир
    start_viewing_button = InlineKeyboardButton(text="Начнем просмотр квартир?", callback_data="view_apartments")
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[[start_viewing_button]])

    await callback_query.message.bot.edit_message_text(
        f"Спасибо! Вот твои параметры:\n\n{result_text}",
        message_id=sent_message_id,
        chat_id=callback_query.message.chat.id,
        reply_markup=keyboard
    )

    await state.clear()





# Хэндлер для начала просмотра квартир
@router.callback_query(lambda c: c.data == "view_apartments")
async def start_viewing_apartments(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    filters = get_user_filters(user_id)

    if not filters:
        await callback_query.message.answer("Вы не задали фильтры. Укажите город и метраж.")
        return

    apartments = get_apartments_by_filter(filters["city"], filters["meters"])
    if apartments:
        await state.update_data(apartments=apartments, current_index=0)
        await show_apartment(callback_query.message, state, apartments[0])
    else:
        await callback_query.message.answer("Нет квартир по заданным параметрам.")


async def show_apartment(message, state, apartment):
    """ Обновляет сообщение с квартирой """

    keyboard = get_feedback_keyboard()
    apartment_info = (
        f"🏠 {apartment[1]}\n"
        f"💰 Цена: {apartment[2]} ₽\n"
        f"📏 Метраж: {apartment[3]} м²\n"
        f"📝 Описание: {apartment[4]}"
    )

    data = await state.get_data()
    message_id = data.get("current_message_id")

    if message_id:
        await message.bot.edit_message_text(apartment_info, chat_id=message.chat.id, message_id=message_id,
                                            reply_markup=keyboard)
    else:
        sent_message = await message.answer(apartment_info, reply_markup=keyboard)
        await state.update_data(current_message_id=sent_message.message_id)

    await state.update_data(current_apartment_id=apartment[0])



@router.callback_query(lambda c: c.data in ["like", "dislike"])
async def process_apartment_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    """ Обрабатывает лайки"""
    user_id = callback_query.from_user.id
    action = callback_query.data

    data = await state.get_data()
    apartments = data.get("apartments", [])
    current_index = data.get("current_index", 0)

    current_apartment_id = data.get("current_apartment_id")

    if current_apartment_id is None:
        await callback_query.answer("Ошибка: не найдена текущая квартира.")
        return

    if action == "like":
        mark_as_liked(user_id, current_apartment_id)
    else:
        mark_as_viewed(user_id, current_apartment_id)

    next_index = current_index + 1


    if next_index < len(apartments):
        next_apartment = apartments[next_index]
        await state.update_data(current_index=next_index, current_apartment_id=next_apartment[0])
        await show_apartment(callback_query.message, state, next_apartment)
    else:
        await callback_query.message.bot.edit_message_text(
            "🏠 Квартиры закончились! Попробуйте изменить фильтр.",
            chat_id=callback_query.message.chat.id,
            message_id=data.get("current_message_id"),
            reply_markup=None
        )
        await state.clear()

    await callback_query.answer()




@router.callback_query(GetApartmentCallbackFactory.filter())
async def get_apartment_callback(callback: CallbackQuery, callback_data: GetApartmentCallbackFactory):

    apartment = get_apartment(callback_data.apartment_id)

    apartment_info = (
        f"🏠 {apartment[1]}\n"
        f"💰 Цена: {apartment[2]} ₽\n"
        f"📏 Метраж: {apartment[3]} м²\n"
        f"📝 Описание: {apartment[4]}"
    )

    await callback.message.answer(apartment_info,
                                       reply_markup=favorite_apartment_selection_kb(
                                           callback_data.user_id, callback_data.apartment_id, callback_data.message_id))




@router.callback_query(DeleteFavoriteCallbackFactory.filter())
async def delete_favorite_callback(callback: CallbackQuery, callback_data: DeleteFavoriteCallbackFactory):
    user_id = callback_data.user_id
    apartment = callback_data.apartment_id
    message_id = callback_data.message_id
    mark_as_unliked(user_id, apartment)


    liked_apartments = get_liked_apartments(user_id)
    keyboard = favorites_kb(liked_apartments, user_id, message_id=message_id)

    await callback.message.delete()
    await callback.message.bot.edit_message_text('Список избранных квартир',
                                                 message_id=message_id,
                                                 chat_id=callback.message.chat.id,
                                                 reply_markup=keyboard)
