from aiogram.fsm.state import StatesGroup, State


class FSMFillFilter(StatesGroup):
    city = State()
    meters = State()


class FSMFillForm(StatesGroup):
    city = State()
    meters = State()
    price = State()
    photo = State()
    title = State()
    description = State()


class FSMEditForm(StatesGroup):
    city = State()
    meters = State()
    price = State()
    photo = State()
    title = State()
    description = State()



