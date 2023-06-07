from aiogram.fsm.state import State, StatesGroup


class ManageSubscriptions(StatesGroup):
    add = State()
    remove = State()
