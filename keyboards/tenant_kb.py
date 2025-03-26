from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.apartments import get_unique_cities
from lexicon.lexicon import LEXICON
from utils.callback_factories import GetApartmentCallbackFactory, DeleteFavoriteCallbackFactory


async def favorites_kb(favorites, user_id, message_id):

    favorites_buttons = [[InlineKeyboardButton(text=f"{row[1]} - {row[2]} руб",
                                                callback_data=GetApartmentCallbackFactory(user_id=user_id,
                                                                                          apartment_id=row[0],
                                                                                          message_id=message_id

                                                                                          ).pack())]
                          for row in favorites]

    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    favorites_keyboard = InlineKeyboardMarkup(inline_keyboard=favorites_buttons + [cancel_btn])

    return favorites_keyboard


async def favorite_apartment_selection_kb(user_id, apartment_id, message_id):
    buttons = [[InlineKeyboardButton(text='Удалить',
                              callback_data=DeleteFavoriteCallbackFactory(
                                  user_id=user_id,
                                  apartment_id=apartment_id,
                                  message_id=message_id)
                              .pack())]]


    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    selection_kb = InlineKeyboardMarkup(inline_keyboard=buttons + [cancel_btn])
    return selection_kb


async def feedback_kb():
    buttons = [
        [InlineKeyboardButton(text="Нравится", callback_data="like")],
        [InlineKeyboardButton(text="Не нравится", callback_data="dislike")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def meters_kb():
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
    return keyboard


async def view_kb():
    start_viewing_button = InlineKeyboardButton(text=LEXICON['press_for_view'], callback_data="view_apartments")
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[[start_viewing_button]])
    return keyboard



async def generate_city_kb():
    """Генерирует клавиатуру на основе уникальных городов из базы данных."""
    cities = get_unique_cities()
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[])

    for city in cities:
        # Создаем кнопку для каждого города
        button = InlineKeyboardButton(text=city, callback_data=city)
        keyboard.inline_keyboard.append([button])

    return keyboard


async def start_view_kb():
    button = InlineKeyboardButton(text=LEXICON['start_view'], callback_data="view_apartments")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard


async def edit_filter_kb():
    button = InlineKeyboardButton(text=LEXICON['edit_filter'], callback_data="start_filter")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard