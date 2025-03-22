from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


from dotenv import load_dotenv

load_dotenv()
router = Router()


@router.callback_query(lambda c: c.data == "list_an_apartment")
def start_landlord_form(callback_query: CallbackQuery, state: FSMContext):
    pass