from aiogram.fsm.state import StatesGroup, State


class FSMFillFilter(StatesGroup):
    city = State()
    meters = State()

