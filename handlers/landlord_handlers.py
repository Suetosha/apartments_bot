import os

from aiogram import Router

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

from dotenv import load_dotenv

from database.apartments import add_apartment, get_apartment_by_id, update_apartment, get_apartment, \
    get_apartments_by_landlord, delete_apartment
from database.users import get_username
from keyboards.landlord_kb import published_apartment_selection_kb, landlord_apartments_kb, confirmation_kb, \
    edit_part_kb
from lexicon.lexicon import LEXICON, get_apartment_info

from utils.callback_factories import EditPublishedApartmentCallbackFactory, GetPublishedApartmentCallbackFactory, \
    DeletePublishedCallbackFactory
from utils.fsm import FSMFillForm, FSMEditForm
from utils.validations import validate_city_name, validate_meters, validate_price, validate_photo

load_dotenv()
router = Router()

FORM_STORAGE = []


@router.callback_query(lambda c: c.data == "list_an_apartment")
async def start_landlord_form(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    chat_id = callback_query.message.chat.id
    await callback_query.message.bot.edit_message_text(
        text=LEXICON['choose_city_landlord'],
        chat_id=chat_id,
        message_id=message_id,
    )
    await state.set_state(FSMFillForm.city)


@router.message(StateFilter(FSMFillForm.city))
async def process_city(message: Message, state: FSMContext):
    city = message.text
    validated_city = validate_city_name(city)

    if validated_city:
        await state.update_data(user_id=message.from_user.id, city=validated_city)
        await state.set_state(FSMFillForm.meters)
        await message.answer(LEXICON['choose_meters_landlord'])
    else:
        await message.answer(LEXICON['city_is_not_found'])


@router.message(StateFilter(FSMFillForm.meters))
async def process_meters(message: Message, state: FSMContext):
    meters = message.text
    if validate_meters(meters):
        await state.update_data(meters=meters)
        await message.answer(LEXICON['choose_price_landlord'])
        await state.set_state(FSMFillForm.price)
    else:
        await message.answer(LEXICON['meters_bad_format'])


@router.message(StateFilter(FSMFillForm.price))
async def process_price(message: Message, state: FSMContext):
    price = message.text
    if validate_price(price):
        await state.update_data(price=price)
        await state.set_state(FSMFillForm.photo)
        await message.answer(LEXICON['send_photo_landlord'])
    else:
        await message.answer(LEXICON['price_bad_format'])



@router.message(StateFilter(FSMFillForm.photo))
async def process_photo(message: Message, state: FSMContext):
    try:
        photo = message.photo[-1]

        if validate_photo(photo):
            file_id = photo.file_id

            # Загружаем файл
            file = await message.bot.get_file(file_id)

            # Указываем временный путь для сохранения в БД (не физически сохраняем в media)
            download_path = os.path.join('media', 'images', f'{file_id}.jpg')

            # Загружаем файл и сохраняем его на сервер
            await message.bot.download_file(file.file_path, download_path)

            # Сохраняем file_id и путь в состоянии
            await state.update_data(photo_file_id=file_id, photo_path=download_path)
            await state.set_state(FSMFillForm.title)
            await message.answer(LEXICON['choose_title_landlord'])
        else:
            await message.answer(LEXICON['photo_bad_format'])
    except TypeError:
        await message.answer('Отправьте фотографию')


@router.message(StateFilter(FSMFillForm.title))
async def process_title(message: Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)
    await state.set_state(FSMFillForm.description)

    await message.answer(text=LEXICON['choose_description_landlord'])


@router.message(StateFilter(FSMFillForm.description))
async def process_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)

    # Получаем данные из состояния
    data = await state.get_data()

    username = get_username(data.get('user_id', 'Не указано'))

    FORM_STORAGE.append(data)

    apartment_info = get_apartment_info(
        city=data.get('city', 'Не указано'),
        title=data.get('title', 'Не указано'),
        price=data.get('price', 'Не указано'),
        meters=data.get('meters', 'Не указано'),
        description=data.get('description', 'Не указано'),
        username=username
    )

    keyboard = confirmation_kb()
    sent_message = await message.answer_photo(
        caption='Спасибо!\n'
                'Объявление, составленное по вашим ответам:\n\n'
                f'{apartment_info}\n\n'
                f'Сохранить?',
        reply_markup=keyboard,
        parse_mode='HTML',
        photo=FSInputFile(path=data['photo_path']),
    )


    await state.update_data(last_message_id=sent_message.message_id)



@router.callback_query(lambda c: c.data == "save_apartment")
async def save_apartment(callback_query: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        await state.clear()

        apartment_id = data.get('apartment_id')
        message_id = data.get("last_message_id")
        del data['last_message_id']
        chat_id = callback_query.message.chat.id

        # Если есть apartment_id, извлекаем квартиру из БД
        if apartment_id:
            apartment = get_apartment_by_id(apartment_id)

            if apartment:
                update_apartment(
                    apartment_id=apartment_id,
                    title=data['title'],
                    price=data['price'],
                    city=data['city'],
                    meters=data['meters'],
                    description=data['description'],
                    photo=data['photo_path'],
                )
                await callback_query.message.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=LEXICON['apartment_updated'],
                    reply_markup=None

                )

        else:
            # Если apartment_id нет, сохраняем новую квартиру
            add_apartment(
                title=data['title'],
                price=data['price'],
                city=data['city'],
                meters=data['meters'],
                description=data['description'],
                user_id=callback_query.from_user.id,
                photo=data['photo_path']
            )

            FORM_STORAGE.remove(data)

            await callback_query.message.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=LEXICON['apartment_saved'],
                reply_markup=None
            )



    except Exception as e:
        print(f"Error: {e}")  # Для отладки
        await callback_query.answer(LEXICON['error'])



@router.callback_query(lambda c: c.data == "edit_apartment")
async def edit_apartment(callback_query: CallbackQuery):
    keyboard = edit_part_kb()
    await callback_query.message.answer(text=LEXICON['choose_part_for_edit'], reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("edit_"))
async def process_edit_choice(callback_query: CallbackQuery, state: FSMContext):
    field_map = {
        "edit_city": FSMEditForm.city,
        "edit_meters": FSMEditForm.meters,
        "edit_price": FSMEditForm.price,
        "edit_title": FSMEditForm.title,
        "edit_description": FSMEditForm.description,
        "edit_photo": FSMEditForm.photo
    }

    field = callback_query.data
    await state.set_state(field_map[field])

    messages = {
        "edit_city": "Введите новый город:",
        "edit_meters": "Введите новое количество метров:",
        "edit_price": "Введите новую цену:",
        "edit_title": "Введите новый заголовок:",
        "edit_description": "Введите новое описание:",
        "edit_photo": "Отправьте новую фотографию"
    }

    await callback_query.message.answer(messages[field])


@router.message(StateFilter(FSMEditForm.city))
async def process_edit_city(message: Message, state: FSMContext):
    validated_city = validate_city_name(message.text)

    if validated_city:
        await state.update_data(city=validated_city)
        await finish_editing(message, state)
    else:
        await message.answer(LEXICON['city_is_not_found'])


@router.message(StateFilter(FSMEditForm.meters))
async def process_edit_meters(message: Message, state: FSMContext):
    meters = message.text
    if validate_meters(meters):
        await state.update_data(meters=meters)
        await finish_editing(message, state)
    else:
        await message.answer(LEXICON['meters_bad_format'])


@router.message(StateFilter(FSMEditForm.price))
async def process_edit_price(message: Message, state: FSMContext):
    price = message.text
    if validate_price(price):
        await state.update_data(price=price)
        await finish_editing(message, state)
    else:
        await message.answer(LEXICON['price_bad_format'])



@router.message(StateFilter(FSMEditForm.photo))
async def process_edit_photo(message: Message, state: FSMContext):
    try:
        photo = message.photo[-1]

        if validate_photo(photo):
            file_id = photo.file_id

            # Загружаем файл
            file = await message.bot.get_file(file_id)

            # Указываем временный путь для сохранения в БД (не физически сохраняем в media)
            download_path = os.path.join('media', 'images', f'{file_id}.jpg')

            # Загружаем файл и сохраняем его на сервер
            await message.bot.download_file(file.file_path, download_path)

            # Сохраняем file_id и путь в состоянии
            await state.update_data(photo_path=download_path)
            await finish_editing(message, state)
        else:
            await message.answer(LEXICON['photo_bad_format'])
    except TypeError:
        await message.answer('Отправьте фотографию')



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
        username = get_username(message.from_user.id)
        apartment_id = data.get('apartment_id')

        if apartment_id:
            # Если apartment_id существует, извлекаем квартиру из БД
            apartment = get_apartment_by_id(apartment_id)

            if not apartment:
                apartment = {}

        else:
            # Если нет apartment_id, используем данные из FORM_STORAGE
            apartment = list(filter(lambda a: a['user_id'] == message.from_user.id, FORM_STORAGE))[0]

        # Обновляем данные квартиры
        apartment.update(data)


        apartment_info = get_apartment_info(
            city=apartment.get('city', 'Не указано'),
            title=apartment.get('title', 'Не указано'),
            price=apartment.get('price', 'Не указано'),
            meters=apartment.get('meters', 'Не указано'),
            description=apartment.get('description', 'Не указано'),
            username=username
        )

        keyboard = confirmation_kb()
        photo_path = data.get('photo_path', apartment['photo_path'])

        sent_message = await message.answer_photo(
            caption=f"Обновленные данные:\n\n{apartment_info}",
            reply_markup=keyboard,
            parse_mode='HTML',
            photo=FSInputFile(photo_path),

        )
        await state.update_data(last_message_id=sent_message.message_id)

    except Exception as e:
        await message.answer(LEXICON['error'])



@router.callback_query(EditPublishedApartmentCallbackFactory.filter())
async def edit_published_apartment_callback(callback_query: CallbackQuery, state: FSMContext):
    apartment_id = callback_query.data.split(":")[1]
    await state.update_data(apartment_id=apartment_id)

    await callback_query.message.answer(LEXICON['choose_part_for_edit'])

    keyboard = edit_part_kb()
    await callback_query.message.answer(LEXICON['choose_part_for_edit'], reply_markup=keyboard)


@router.callback_query(GetPublishedApartmentCallbackFactory.filter())
async def get_published_apartment_callback(callback: CallbackQuery,
                                           callback_data: GetPublishedApartmentCallbackFactory):
    apartment = get_apartment(callback_data.apartment_id)
    username = get_username(apartment[1])

    apartment_info = get_apartment_info(
        city=apartment[4],
        title=apartment[2],
        price=apartment[3],
        meters=apartment[5],
        description=apartment[6],
        username=username

    )

    keyboard = published_apartment_selection_kb(callback_data.apartment_id,callback_data.message_id)

    await callback.message.answer_photo(
                                  caption=apartment_info,
                                  photo=FSInputFile(apartment[7]),
                                  parse_mode='HTML',
                                  reply_markup=keyboard)




@router.callback_query(DeletePublishedCallbackFactory.filter())
async def delete_favorite_callback(callback: CallbackQuery, callback_data: DeletePublishedCallbackFactory):
    user_id = callback.from_user.id
    apartment_id = callback_data.apartment_id
    message_id = callback_data.message_id

    delete_apartment(apartment_id)

    published_apartments = get_apartments_by_landlord(user_id)
    keyboard = landlord_apartments_kb(published_apartments, message_id)

    await callback.message.delete()
    await callback.message.bot.edit_message_text(LEXICON['apartments_list'],
                                                 message_id=message_id,
                                                 chat_id=callback.message.chat.id,
                                                 reply_markup=keyboard)
