from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.callback_factories import GetPublishedApartmentCallbackFactory, EditPublishedApartmentCallbackFactory, \
    DeletePublishedCallbackFactory


def landlord_apartments_kb(apartments, message_id):
    """Создаёт клавиатуру с квартирами арендодателя и кнопкой 'Отменить'"""

    apartments_buttons = [
        [InlineKeyboardButton(
            text=f"{row[2]} - {row[3]} руб",
            callback_data=GetPublishedApartmentCallbackFactory(
                apartment_id=row[0],
                message_id=message_id
            ).pack()
        )]
        for row in apartments
    ]

    # Кнопка отменить
    action_buttons = [
        InlineKeyboardButton(text='Отменить', callback_data='cancel')
    ]

    landlord_keyboard = InlineKeyboardMarkup(inline_keyboard=apartments_buttons + [action_buttons])

    return landlord_keyboard


def landlord_apartment_selection_kb(user_id, apartment_id, message_id):
    """Создаёт клавиатуру с кнопками 'Изменить' и 'Отменить' для арендодателя."""

    buttons = [[InlineKeyboardButton(
        text='Изменить',
        callback_data=EditPublishedApartmentCallbackFactory(
            user_id=user_id,
            apartment_id=apartment_id,
            message_id=message_id
        ).pack()
    )]]

    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    selection_kb = InlineKeyboardMarkup(inline_keyboard=buttons + [cancel_btn])
    return selection_kb



def published_apartment_selection_kb(apartment_id, message_id):
    buttons = [[InlineKeyboardButton(text='Удалить',
                              callback_data=DeletePublishedCallbackFactory(
                                  apartment_id=apartment_id,
                                  message_id=message_id
                              )
                              .pack())]]


    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    selection_kb = InlineKeyboardMarkup(inline_keyboard=buttons + [cancel_btn])
    return selection_kb


def confirmation_kb():
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data='save_apartment')],
        [InlineKeyboardButton(text="Изменить", callback_data='edit_apartment')],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def edit_part_kb():
    buttons = [
        [InlineKeyboardButton(text="🏙 Город", callback_data="edit_city")],
        [InlineKeyboardButton(text="📏 Метры", callback_data="edit_meters")],
        [InlineKeyboardButton(text="💰 Цена", callback_data="edit_price")],
        [InlineKeyboardButton(text="📝 Заголовок", callback_data="edit_title")],
        [InlineKeyboardButton(text="📃 Описание", callback_data="edit_description")],
        [InlineKeyboardButton(text="📷 Фото", callback_data="edit_photo")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard