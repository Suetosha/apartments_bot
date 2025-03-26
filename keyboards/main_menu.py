from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton

# Лексикон команд
COMMAND_LEXICON = {
    '/filter': 'Ваш фильтр для поиска квартир',
    '/favorites': 'Посмотреть избранные квартиры',
    '/view_apartments': 'Поиск квартир по фильтру',
    '/publish_apartment': 'Опубликовать квартиру',
    '/view_published_apartments': 'Посмотреть опубликованные квартиры'
}


# Функция для установки команд в главное меню
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/filter', description=COMMAND_LEXICON['/filter']),
        BotCommand(command='/favorites', description=COMMAND_LEXICON['/favorites']),
        BotCommand(command="/view_apartments", description=COMMAND_LEXICON['/view_apartments']),
        BotCommand(command="/publish_apartment", description=COMMAND_LEXICON['/publish_apartment']),
        BotCommand(command="/view_published_apartments", description=COMMAND_LEXICON['/view_published_apartments']),

    ]
    await bot.set_my_commands(main_menu_commands)



async def options_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="Найти квартиру", callback_data="start_filter")],
        [InlineKeyboardButton(text="Сдать квартиру", callback_data="list_an_apartment")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


