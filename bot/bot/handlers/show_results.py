from aiogram import F, Router, methods
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from messages import message_generate
from constants import (
    SEARCH_OR_EDIT,
)
import keyboards as kb

show_results_router = Router()


@show_results_router.callback_query(
    F.data.in_({SEARCH_OR_EDIT['EN'][0], SEARCH_OR_EDIT['RU'][0]})
)
async def show_results(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    This handler shows real estate objects.
    """

    await callback.message.delete()
    await message_generate(step_name='show_results', callback=callback)


@show_results_router.callback_query(
    F.data.func(lambda data: data.isdigit())
)
async def pagination(
    callback: CallbackQuery
) -> None:
    await callback.message.delete()
    await message_generate(step_name='pagination', callback=callback)
