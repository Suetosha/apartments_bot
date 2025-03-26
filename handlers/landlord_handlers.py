import os

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile

from database.apartments import *
from database.users import get_username

from keyboards.landlord_kb import *

from lexicon.lexicon import LEXICON, get_apartment_info

from utils.callback_factories import GetPublishedApartmentCallbackFactory, DeletePublishedCallbackFactory
from utils.fsm import FSMFillForm
from utils.validations import *

router = Router()


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


#                          Заполнение/редактирование формы

@router.message(StateFilter(FSMFillForm.city))
async def process_city(message: Message, state: FSMContext):
    city = message.text
    validated_city = validate_city_name(city)
    data = await state.get_data()

    if validated_city:
        # Если это редактирование
        if data.get('edit_mode'):
            await state.update_data(city=validated_city)
            await message.answer("Город обновлен")
            await finish_process(message, state)
        else:
            # Если это первое заполнение
            await state.update_data(city=validated_city)
            await state.set_state(FSMFillForm.meters)
            await message.answer(LEXICON['choose_meters_landlord'])

    else:
        await message.answer(LEXICON['city_is_not_found'])


@router.message(StateFilter(FSMFillForm.meters))
async def process_meters(message: Message, state: FSMContext):
    meters = message.text

    if validate_meters(meters):
        data = await state.get_data()

        # Если это редактирование
        if data.get('edit_mode'):
            await state.update_data(meters=meters)
            await message.answer("Площадь обновлена")
            await finish_process(message, state)
        else:
            # Если это первый ввод
            await state.update_data(meters=meters)
            await message.answer(LEXICON['choose_price_landlord'])
            await state.set_state(FSMFillForm.price)

    else:
        await message.answer(LEXICON['meters_bad_format'])


@router.message(StateFilter(FSMFillForm.price))
async def process_price(message: Message, state: FSMContext):
    price = message.text

    if validate_price(price):
        data = await state.get_data()

        # Если это редактирование
        if data.get('edit_mode'):
            await state.update_data(price=price)
            await message.answer("Цена обновлена")
            await finish_process(message, state)
        else:
            # Если это первый ввод
            await state.update_data(price=price)
            await state.set_state(FSMFillForm.photo)
            await message.answer(LEXICON['send_photo_landlord'])

    else:
        await message.answer(LEXICON['price_bad_format'])


@router.message(StateFilter(FSMFillForm.photo))
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()

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

            # Если это редактирование
            if data.get('edit_mode'):
                await message.answer("Фото обновлено")
                await finish_process(message, state)
            else:
                # Если это первый ввод
                await state.set_state(FSMFillForm.title)
                await message.answer(LEXICON['choose_title_landlord'])

        else:
            await message.answer(LEXICON['photo_bad_format'])
    except TypeError:
        await message.answer('Отправьте фотографию')


@router.message(StateFilter(FSMFillForm.title))
async def process_title(message: Message, state: FSMContext):
    data = await state.get_data()
    title = message.text
    await state.update_data(title=title)
    user_id = message.from_user.id

    # Если это редактирование (есть apartment_id), завершаем процесс
    if data.get('edit_mode'):
        await message.answer("Заголовок обновлен")
        await finish_process(message, state)
    else:
        # Если это первый ввод
        await state.set_state(FSMFillForm.description)
        await message.answer(text=LEXICON['choose_description_landlord'])


@router.message(StateFilter(FSMFillForm.description))
async def process_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)

    data = await state.get_data()

    # Если это редактирование (есть apartment_id), завершаем процесс
    if data.get('edit_mode'):
        await message.answer("Описание обновлено")
        await finish_process(message, state)
    else:
        await state.set_state(FSMFillForm.confirmation)
        await message.answer(LEXICON['confirmation_landlord'])
        await finish_process(message, state)


@router.message(StateFilter(FSMFillForm.confirmation))
async def finish_process(message: Message, state: FSMContext):
    try:
        data = await state.get_data()

        apartment_info = get_apartment_info(
            city=data['city'],
            title=data['title'],
            price=data['price'],
            meters=data['meters'],
            description=data['description'],
            username=get_username(message.from_user.id)
        )

        keyboard = confirmation_kb()
        photo_path = data.get('photo_path')

        sent_message = await message.answer_photo(
            caption='Спасибо!\n'
                    'Объявление, составленное по вашим ответам:\n\n'
                    f'{apartment_info}\n\n'
                    f'Сохранить?',
            reply_markup=keyboard,
            parse_mode='HTML',
            photo=FSInputFile(photo_path),

        )
        await state.update_data(last_message_id=sent_message.message_id)

    except Exception as e:
        await message.answer(LEXICON['error'])


#                             Сохранение формы
@router.callback_query(lambda c: c.data == "save_apartment")
async def save_apartment(callback_query: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        # Сохраняем новую квартиру
        add_apartment(
            title=data['title'],
            price=data['price'],
            city=data['city'],
            meters=data['meters'],
            description=data['description'],
            user_id=callback_query.from_user.id,
            photo=data['photo_path']
        )

        await state.clear()

        await callback_query.message.bot.edit_message_caption(
            chat_id=callback_query.message.chat.id,
            message_id=data.get("last_message_id"),
            caption=LEXICON['apartment_saved'],
            reply_markup=None
        )


    except Exception as e:
        print(f"Error: {e}")
        await callback_query.answer(LEXICON['error'])


#                            Изменение формы
@router.callback_query(lambda c: c.data == "edit_apartment")
async def edit_apartment(callback_query: CallbackQuery):
    keyboard = edit_part_kb()
    await callback_query.message.answer(text=LEXICON['choose_part_for_edit'], reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("edit_"))
async def process_edit_choice(callback_query: CallbackQuery, state: FSMContext):
    field_map = {
        "edit_city": FSMFillForm.city,
        "edit_meters": FSMFillForm.meters,
        "edit_price": FSMFillForm.price,
        "edit_title": FSMFillForm.title,
        "edit_description": FSMFillForm.description,
        "edit_photo": FSMFillForm.photo
    }

    field = callback_query.data
    await state.set_state(field_map[field])
    await state.update_data(edit_mode=True)

    messages = {
        "edit_city": "Введите новый город:",
        "edit_meters": "Введите новое количество метров:",
        "edit_price": "Введите новую цену:",
        "edit_title": "Введите новый заголовок:",
        "edit_description": "Введите новое описание:",
        "edit_photo": "Отправьте новую фотографию"
    }

    await callback_query.message.answer(messages[field])


#                              Получение и удаление опубликованных квартир
@router.callback_query(GetPublishedApartmentCallbackFactory.filter())
async def get_published_apartment_callback(callback: CallbackQuery,
                                           callback_data: GetPublishedApartmentCallbackFactory):
    try:
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

        keyboard = published_apartment_selection_kb(callback_data.apartment_id, callback_data.message_id)

        await callback.message.answer_photo(
            caption=apartment_info,
            photo=FSInputFile(apartment[7]),
            parse_mode='HTML',
            reply_markup=keyboard)
    except Exception as error:
        print(error)
        await callback.answer(LEXICON['error'])


@router.callback_query(DeletePublishedCallbackFactory.filter())
async def delete_published_callback(callback: CallbackQuery, callback_data: DeletePublishedCallbackFactory):
    try:
        user_id = callback.from_user.id
        apartment_id = callback_data.apartment_id
        message_id = callback_data.message_id

        delete_apartment(apartment_id)

        published_apartments = get_apartments_by_landlord(user_id)
        keyboard = published_apartments_kb(published_apartments, message_id)

        await callback.message.delete()
        await callback.message.bot.edit_message_text(LEXICON['apartments_list'],
                                                     message_id=message_id,
                                                     chat_id=callback.message.chat.id,
                                                     reply_markup=keyboard)
    except Exception as error:
        print(error)
        await callback.answer(LEXICON['error'])
