from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from dotenv import load_dotenv

from database.apartments import add_apartment
from utils.callback_factories import EditPublishedApartmentCallbackFactory
from utils.fsm import FSMFillForm, FSMEditForm

load_dotenv()
router = Router()


FORM_STORAGE = []

@router.callback_query(lambda c: c.data == "list_an_apartment")
async def start_landlord_form(callback_query: CallbackQuery, state: FSMContext):

    await callback_query.message.answer(
        text='В каком городе вы хотите сдавать квартиру?',
    )

    await state.set_state(FSMFillForm.city)



@router.message(StateFilter(FSMFillForm.city))
async def process_city(message: Message, state: FSMContext):

    city = message.text

    await state.update_data(user_id=message.from_user.id, city=city)

    await state.set_state(FSMFillForm.meters)

    await message.answer(
        "Сколько метров в квартире?",
    )




@router.message(StateFilter(FSMFillForm.meters))
async def process_meters(message: Message, state: FSMContext):
    meters = message.text
    await state.update_data(meters=meters)

    await message.answer(
        "За сколько вы бы хотели её сдавать?",
    )

    await state.set_state(FSMFillForm.price)



@router.message(StateFilter(FSMFillForm.price))
async def process_price(message: Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)

    await state.set_state(FSMFillForm.title)

    await message.answer(
        "Напишите заголовок для вашего объявления",
    )



@router.message(StateFilter(FSMFillForm.title))
async def process_title(message: Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)
    await state.set_state(FSMFillForm.description)

    await message.answer(
        text='Напишите описание для вашего объявления',
    )


@router.message(StateFilter(FSMFillForm.description))
async def process_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)

    # Получаем данные из состояния
    data = await state.get_data()
    del data['message_id']

    await state.clear()

    FORM_STORAGE.append(data)

    apartment_info = (
        f"🏠 {data.get('title', 'Не указано')}\n"
        f"💰 Цена: {data.get('price', 'Не указано')} ₽\n"
        f"📏 Метры: {data.get('meters', 'Не указано')} м²\n"
        f"📝 Описание: {data.get('description', 'Не указано')}"
    )


    buttons = [
        [InlineKeyboardButton(text="Да", callback_data='save_apartment')],


        [InlineKeyboardButton(text="Изменить", callback_data='edit_apartment')],
    ]


    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)


    await message.answer(
        text='Спасибо!\n'
             'Объявление, составленное по вашим ответам:\n\n'
             f'{apartment_info}\n\n'
             f'Сохранить?',
        reply_markup=keyboard

    )

@router.callback_query(lambda c: c.data == "save_apartment")
async def save_apartment(callback_query: CallbackQuery):
    try:
        apartment = list(filter(lambda a: a['user_id'] == callback_query.from_user.id, FORM_STORAGE))[0]

        add_apartment(title=apartment['title'],
                      price=apartment['price'],
                      city=apartment['city'],
                      meters=apartment['meters'],
                      description=apartment['description'],
                      user_id=apartment['user_id'])

        FORM_STORAGE.remove(apartment)
        await callback_query.message.answer('Квартира успешно сохранена')
    except IndexError:
        await callback_query.answer('Что-то пошло не так, попробуйте через несколько минут')


@router.callback_query(lambda c: c.data == "edit_apartment")
async def edit_apartment(callback_query: CallbackQuery):

    text = 'Что нужно изменить?'

    buttons = [
        [InlineKeyboardButton(text="🏙 Город", callback_data="edit_city")],
        [InlineKeyboardButton(text="📏 Метры", callback_data="edit_meters")],
        [InlineKeyboardButton(text="💰 Цена", callback_data="edit_price")],
        [InlineKeyboardButton(text="📝 Заголовок", callback_data="edit_title")],
        [InlineKeyboardButton(text="📃 Описание", callback_data="edit_description")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback_query.message.answer(text=text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("edit_"))
async def process_edit_choice(callback_query: CallbackQuery, state: FSMContext):
    field_map = {
        "edit_city": FSMEditForm.city,
        "edit_meters": FSMEditForm.meters,
        "edit_price": FSMEditForm.price,
        "edit_title": FSMEditForm.title,
        "edit_description": FSMEditForm.description,
    }

    field = callback_query.data
    await state.set_state(field_map[field])

    messages = {
        "edit_city": "Введите новый город:",
        "edit_meters": "Введите новое количество метров:",
        "edit_price": "Введите новую цену:",
        "edit_title": "Введите новый заголовок:",
        "edit_description": "Введите новое описание:",
    }

    await callback_query.message.answer(messages[field])



@router.message(StateFilter(FSMEditForm.city))
async def process_edit_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await finish_editing(message, state)


@router.message(StateFilter(FSMEditForm.meters))
async def process_edit_meters(message: Message, state: FSMContext):
    await state.update_data(meters=message.text)
    await finish_editing(message, state)


@router.message(StateFilter(FSMEditForm.price))
async def process_edit_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await finish_editing(message, state)


@router.message(StateFilter(FSMEditForm.title))
async def process_edit_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await finish_editing(message, state)


@router.message(StateFilter(FSMEditForm.description))
async def process_edit_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await finish_editing(message, state)



async def finish_editing(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        apartment = list(filter(lambda a: a['user_id'] == message.from_user.id, FORM_STORAGE))[0]
        apartment.update(data)


        apartment_info = (
            f"🏠 {apartment.get('title', 'Не указано')}\n"
            f"💰 Цена: {apartment.get('price', 'Не указано')} ₽\n"
            f"📏 Метры: {apartment.get('meters', 'Не указано')} м²\n"
            f"📝 Описание: {apartment.get('description', 'Не указано')}"
        )

        buttons = [
            [InlineKeyboardButton(text="✅ Сохранить", callback_data="save_apartment")],
            [InlineKeyboardButton(text="🔄 Изменить снова", callback_data="edit_apartment")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            text=f"Обновленные данные:\n\n{apartment_info}",
            reply_markup=keyboard
        )

        await state.clear()
    except IndexError:
        await message.answer('Что-то пошло не так, попробуйте через несколько минут')


@router.callback_query(EditPublishedApartmentCallbackFactory.filter())
async def edit_published_apartment_callback(callback_query: CallbackQuery, state: FSMContext):
    pass







