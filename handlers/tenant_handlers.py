from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto


from database.activity import *
from database.apartments import get_apartments_by_filter, get_apartment
from database.users import get_username
from keyboards.tenant_kb import feedback_kb, favorite_apartment_selection_kb, favorites_kb, \
    meters_kb, view_kb, generate_city_kb
from lexicon.lexicon import LEXICON, get_apartment_info, get_result_text
from utils.callback_factories import GetApartmentCallbackFactory, DeleteFavoriteCallbackFactory
from utils.fsm import FSMFillFilter

from database.filter import save_filter, get_user_filters


router = Router()


# Хэндлер для начала заполнения формы
@router.callback_query(lambda c: c.data == "start_filter")
async def start_fill_form(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")
    keyboard = generate_city_kb()

    sent_message = await callback_query.message.bot.edit_message_text(
        text=LEXICON['choose_city_tenant'],
        message_id=sent_message_id,
        chat_id=callback_query.message.chat.id,
        reply_markup=keyboard,
    )

    await state.update_data(message_id=sent_message.message_id)
    await state.set_state(FSMFillFilter.city)


# Хэндлер для получения города
@router.callback_query(StateFilter(FSMFillFilter.city))
async def process_city(callback_query: CallbackQuery, state: FSMContext):
    city = callback_query.data
    await state.update_data(city=city)

    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")

    keyboard = meters_kb()

    sent_message = await callback_query.message.bot.edit_message_text(
        LEXICON['choose_meters_tenant'],
        message_id=sent_message_id,
        chat_id=callback_query.message.chat.id,
        reply_markup=keyboard
    )

    await state.update_data(message_id=sent_message.message_id)
    await state.set_state(FSMFillFilter.meters)


# Хэндлер для получения метража
@router.callback_query(StateFilter(FSMFillFilter.meters))
async def process_meters(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sent_message_id = user_data.get("message_id")
    user_id = callback_query.from_user.id

    meters = callback_query.data
    data = await state.get_data()

    await state.update_data(meters=meters)

    save_filter(user_id, data.get('city'), meters)

    result_text = get_result_text(data.get('city'), meters)
    keyboard = view_kb()

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
        await callback_query.message.answer(LEXICON['filter_doesnt_exist'])
        return

    apartments = get_apartments_by_filter(filters["city"], filters["meters"])
    apartments = list(filter(lambda a: not is_apartment_viewed(user_id, a[0]), apartments))

    if apartments:
        await state.update_data(apartments=apartments, current_index=0)
        await show_apartment(callback_query.message, state, apartments[0])
    else:
        await callback_query.message.answer(LEXICON['apartments_doesnt_exist'])


# Функция для обновления сообщения с квартирой
async def show_apartment(message, state, apartment):

    keyboard = feedback_kb()
    username = get_username(apartment[1])

    photo_path = apartment[7]

    apartment_info = get_apartment_info(
        city=apartment[4],
        title=apartment[2],
        price=apartment[3],
        meters=apartment[5],
        description=apartment[6],
        username=username
    )

    data = await state.get_data()
    message_id = data.get("current_message_id")
    try:
        if message_id:

            await message.bot.edit_message_media(
                                                chat_id=message.chat.id,
                                                message_id=message_id,
                                                media=InputMediaPhoto(
                                                    media=FSInputFile(photo_path),
                                                    caption=apartment_info,
                                                    parse_mode = "HTML"
                                                ),
                                                reply_markup=keyboard
                                                 )
        else:

            sent_message = await message.answer_photo(
                caption=apartment_info,
                reply_markup=keyboard,
                parse_mode='HTML',
                photo=FSInputFile(photo_path),
            )

            await state.update_data(current_message_id=sent_message.message_id)

    except Exception as error:
        print('error', error)

    await state.update_data(current_apartment_id=apartment[0])


# Хэндлер для обработки лайков и смены квартиры за счет индекса
@router.callback_query(lambda c: c.data in ["like", "dislike"])
async def process_apartment_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    action = callback_query.data

    data = await state.get_data()
    apartments = data.get("apartments", [])
    current_index = data.get("current_index", 0)

    current_apartment_id = data.get("current_apartment_id")

    if current_apartment_id is None:
        await callback_query.answer(LEXICON['error_apartment'])
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

        await callback_query.message.bot.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=data.get("current_message_id"),
            media=InputMediaPhoto(
                media=FSInputFile("media/images/end.png"),
                caption=LEXICON['apartments_sold_out'],
                parse_mode="HTML"
            ),
            reply_markup=None
        )
        await state.clear()

    await callback_query.answer()


# Хэндлер для получения избранной квартиры
@router.callback_query(GetApartmentCallbackFactory.filter())
async def get_apartment_callback(callback: CallbackQuery, callback_data: GetApartmentCallbackFactory):
    apartment = get_apartment(callback_data.apartment_id)
    username = get_username(apartment[1])

    apartment_info = get_apartment_info(
        city=apartment[4],
        title=apartment[2],
        price=apartment[3],
        meters=apartment[5],
        description=apartment[6],
        username=username,

    )
    keyboard = favorite_apartment_selection_kb(callback_data.user_id,
                                               callback_data.apartment_id,
                                               callback_data.message_id
                                               )

    await callback.message.answer_photo(
                                  photo=FSInputFile(apartment[7]),
                                  caption=apartment_info,
                                  parse_mode='HTML',
                                  reply_markup=keyboard)


# Хэндлер для удаления избранной квартиры
@router.callback_query(DeleteFavoriteCallbackFactory.filter())
async def delete_favorite_callback(callback: CallbackQuery, callback_data: DeleteFavoriteCallbackFactory):
    user_id = callback_data.user_id
    apartment_id = callback_data.apartment_id
    message_id = callback_data.message_id
    mark_as_unliked(user_id, apartment_id)

    liked_apartments = get_liked_apartments(user_id)
    keyboard = favorites_kb(liked_apartments, user_id, message_id=message_id)

    await callback.message.delete()
    await callback.message.bot.edit_message_text(LEXICON['apartments_list'],
                                                 message_id=message_id,
                                                 chat_id=callback.message.chat.id,
                                                 reply_markup=keyboard)
