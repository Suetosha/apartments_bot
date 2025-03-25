from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dotenv import load_dotenv
from lexicon.lexicon import LEXICON


load_dotenv()
router = Router()

@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.delete()


@router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(LEXICON['help'])


@router.message()
async def process_other_command(message: Message):
    await message.answer(LEXICON['other'])