import asyncio
import os

from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

from handlers import tenant_handlers, main_handlers, landlord_handlers

from database.create_tables import init_db
from keyboards.main_menu import set_main_menu

load_dotenv()


async def main() -> None:
    try:
        token = os.getenv('TOKEN')

        bot = Bot(token=token)
        dp = Dispatcher()

        await set_main_menu(bot)

        init_db()
        # load_apartments_from_csv()

        dp.include_router(main_handlers.router)
        dp.include_router(landlord_handlers.router)
        dp.include_router(tenant_handlers.router)


        await dp.start_polling(bot)

    except Exception as error:
        print(error)


if __name__ == '__main__':
    asyncio.run(main())
