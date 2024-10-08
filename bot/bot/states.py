from aiogram.fsm.state import State, StatesGroup


class SerachParametersData(StatesGroup):
    language = State()

    city_first_letter = State()
    city = State()

    property_type = State()
    number_of_rooms = State()

    min_square = State()
    max_square = State()

    min_price = State()
    max_price = State()

    min_square_question = State()
    max_square_question = State()
    min_price_question = State()
    max_price_question = State()


class EditSearchParametersData(StatesGroup):
    language = State()

    city_first_letter = State()
    city = State()

    property_type = State()
    number_of_rooms = State()

    min_square = State()
    max_square = State()

    min_price = State()
    max_price = State()

    min_square_question = State()
    max_square_question = State()
    min_price_question = State()
    max_price_question = State()
