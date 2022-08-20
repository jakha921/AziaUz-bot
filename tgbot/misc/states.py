from aiogram.dispatcher.filters.state import State, StatesGroup


class ContactVerify(StatesGroup):
    token = State()


class Feedback(StatesGroup):
    feedback = State()


class UserDetails(StatesGroup):
    first_name = State()
    last_name = State()
    dob = State()
    gender = State()
    marital_status = State()
    occupation = State()

