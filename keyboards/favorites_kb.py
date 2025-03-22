from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.callback_factories import GetApartmentCallbackFactory, DeleteFavoriteCallbackFactory


def favorites_kb(favorites, user_id, message_id):

    favorites_buttons = [[InlineKeyboardButton(text=f"{row[1]} - {row[2]} руб",
                                                callback_data=GetApartmentCallbackFactory(user_id=user_id,
                                                                                          apartment_id=row[0],
                                                                                          message_id=message_id

                                                                                          ).pack())]
                          for row in favorites]

    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    favorites_keyboard = InlineKeyboardMarkup(inline_keyboard=favorites_buttons + [cancel_btn])

    return favorites_keyboard


def favorite_apartment_selection_kb(user_id, apartment_id, message_id):
    buttons = [[InlineKeyboardButton(text='Удалить',
                              callback_data=DeleteFavoriteCallbackFactory(
                                  user_id=user_id,
                                  apartment_id=apartment_id,
                                  message_id=message_id)
                              .pack())]]


    cancel_btn = [InlineKeyboardButton(text='Отменить', callback_data='cancel')]

    selection_kb = InlineKeyboardMarkup(inline_keyboard=buttons + [cancel_btn])
    return selection_kb
