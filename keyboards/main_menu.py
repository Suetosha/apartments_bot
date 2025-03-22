from aiogram import Bot
from aiogram.types import BotCommand



# Лексикон команд
COMMAND_LEXICON = {
    '/filter': 'Ваш фильтр для поиска квартир',
    '/favorites': 'Посмотреть избранные квартиры',
    '/view_apartments': 'Поиск квартир по фильтру'
}


# Функция для установки команд в главное меню
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/filter', description=COMMAND_LEXICON['/filter']),
        BotCommand(command='/favorites', description=COMMAND_LEXICON['/favorites']),
        BotCommand(command="/view_apartments", description=COMMAND_LEXICON['/view_apartments']),
    ]
    await bot.set_my_commands(main_menu_commands)