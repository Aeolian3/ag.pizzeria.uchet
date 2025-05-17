from aiogram.fsm.state import StatesGroup, State

class InventoryStates(StatesGroup):
    waiting_for_quantity = State()
    choose_frequency = State()
    waiting_for_pin = State()



