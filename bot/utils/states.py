from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    choosing_type = State()
    waiting_content = State()
    confirming = State()


class ChannelStates(StatesGroup):
    waiting_channel = State()


class UserSearchStates(StatesGroup):
    waiting_id = State()
