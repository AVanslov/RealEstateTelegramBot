import json

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from api_requests import make_request
from constants import SEARCH_OR_EDIT, CITIES, GET_CITIES, get_cities
from settings import DEBAG


async def make_inline_pagination_buttons(results, current_obj_index):
    buttons = {}
    if current_obj_index - 1 in range(0, len(results)):
        buttons['⬅️'] = str(current_obj_index - 1)
    else:
        buttons[' '] = 'NoData'

    buttons[str(current_obj_index + 1) + '/' + str(len(results))] = 'NoData'

    if current_obj_index + 1 in range(0, len(results)):
        buttons['➡️'] = str(current_obj_index + 1)
    else:
        buttons[' '] = 'NoData'
    buttons[SEARCH_OR_EDIT['EN'][1]] = SEARCH_OR_EDIT['EN'][1]
    return buttons


async def make_inline_keyboard(
    data: list = None,
    raws: int = 1,
    data_with_callback: dict = None
) -> InlineKeyboardMarkup:
    """
    Receives a list as input and divides it into lists
    by the specified number of elements,
    then forms a keyboard layout object in the form of a grid.
    """
    if data_with_callback is None:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i,
                        callback_data=i
                    ) for i in data[i:i + raws]
                ] for i in range(0, len(data), raws)
            ]
        )
    else:
        data = list(data_with_callback.keys())
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i,
                        callback_data=data_with_callback[i]
                    ) for i in data[i:i + raws]
                ] for i in range(0, len(data), raws)
            ]
        )


async def cities(first_letter: str) -> InlineKeyboardMarkup:
    """
    Return InlineKeyboardMurkup with
    cities starting with the selected letter.
    """
    cities = await get_cities()
    return await make_inline_keyboard(
        [i for i in cities if i[:1] == first_letter], 2
    )
