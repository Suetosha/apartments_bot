from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_feedback_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Нравится", callback_data="like")],
        [InlineKeyboardButton(text="Не нравится", callback_data="dislike")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard