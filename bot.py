import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from database.apartments import load_apartments_from_csv
from handlers import tenant_handlers, main_handlers, landlord_handlers, other_handlers

from database.create_tables import init_db
from keyboards.main_menu import set_main_menu

load_dotenv()


async def start_bot() -> None:
    while True:
        try:
            token = os.getenv('TOKEN')
            if not token:
                raise ValueError("Отсутствует токен бота!")

            bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
            dp = Dispatcher()

            await set_main_menu(bot)
            init_db()

            dp.include_router(main_handlers.router)
            dp.include_router(landlord_handlers.router)
            dp.include_router(tenant_handlers.router)
            dp.include_router(other_handlers.router)

            #load_apartments_from_csv()

            logging.info("Бот запущен!")
            await dp.start_polling(bot)

        except Exception as error:
            logging.error(f"Ошибка в работе бота: {error}", exc_info=True)
            await asyncio.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")
