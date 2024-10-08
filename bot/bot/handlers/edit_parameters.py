import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from api_requests import (
    GET_OR_CREATE_SEARCH_PARAMETER,
    make_request
)
from constants import (
    SEARCH_OR_EDIT,
    SEARCH_PARAMETERS,
)
from messages import message_generate
from serializers import DATA
from states import EditSearchParametersData
from validators import max_value_validation_error

edit_parameters_router = Router()


async def update_data_in_api(
    state,
    message=None,
    callback=None,
):
    if callback is not None:
        telegram_id = callback.from_user.id
    else:
        telegram_id = message.from_user.id

    data = await state.get_data()

    try:
        response = await make_request(
            method='POST',
            path=GET_OR_CREATE_SEARCH_PARAMETER,
            json={
                'customer': telegram_id,
                'category': data['property_type'],
                'city': data['city'],
                'min_price': data['min_price'],
                'max_price': data['max_price'],
                'min_area': data['min_square'],
                'max_area': data['max_square'],
                'rooms_number': data['number_of_rooms'],
            }
        )
        logging.debug(
            'The attempt to update the city'
            f'field ended with the status {response.status}'
        )
    except ConnectionError as e:
        logging.debug(e)


@edit_parameters_router.callback_query(
    F.data.in_({SEARCH_OR_EDIT['EN'][1], SEARCH_OR_EDIT['RU'][1]})
)
async def show_results(
    callback: CallbackQuery
) -> None:
    """
    This handler allows you to select an item to edit.
    """

    await callback.message.delete()
    await message_generate(
        step_name='select_field_for_edit',
        callback=callback,
    )


@edit_parameters_router.callback_query(
    F.data.in_(set(list(SEARCH_PARAMETERS.keys())))
)
async def edit_field(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    This handler allows you to select an item to edit.
    """
    await callback.message.delete()
    await message_generate(
        step_name='edit_selected_field',
        callback=callback,
        state=state
    )


@edit_parameters_router.callback_query(
    EditSearchParametersData.city_first_letter
)
async def edit_city(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Allow to select city name based on selected letter.
    """
    await state.update_data(city_first_letter=callback.data)
    logging.debug(
        'Edit has been started: '
        f'User select city first letter - {callback.data}'
    )
    await callback.message.delete()
    await state.set_state(EditSearchParametersData.city)
    await message_generate(
        step_name='edit_city', callback=callback, state=state
    )


@edit_parameters_router.callback_query(
    EditSearchParametersData.city
)
async def get_city(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Allow user to continue edit parameters or see results.
    """
    await state.update_data(city=callback.data)

    await update_data_in_api(callback=callback, state=state)

    await state.clear()

    await callback.message.delete()
    await message_generate(
        step_name='continue_edit_or_search',
        callback=callback
    )


@edit_parameters_router.callback_query(
    EditSearchParametersData.property_type
)
async def get_property_type(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Allow user to continue edit parameters or see results.
    """
    await state.update_data(property_type=callback.data)

    await update_data_in_api(callback=callback, state=state)

    await state.clear()

    await callback.message.delete()
    await message_generate(
        step_name='continue_edit_or_search',
        callback=callback
    )


@edit_parameters_router.callback_query(
    EditSearchParametersData.number_of_rooms
)
async def get_number_of_rooms(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Allow user to continue edit parameters or see results.
    """
    await state.update_data(number_of_rooms=callback.data)

    await update_data_in_api(callback=callback, state=state)

    await state.clear()

    await callback.message.delete()
    await message_generate(
        step_name='continue_edit_or_search',
        callback=callback
    )


@edit_parameters_router.message(
    EditSearchParametersData.min_square
)
async def get_min_square(
    message: Message,
    state: FSMContext
) -> None:
    """
    Allow user to continue edit parameters or see results.
    """
    if (lambda value: value.isdigit() and (
            int(value) < 2147483647))(message.text):
        await state.update_data(min_square=message.text)

        await update_data_in_api(message=message, state=state)

        await state.clear()

        DATA['min_square'] = message.text
        await message.delete()
        await message_generate(
            step_name='continue_edit_or_search', message=message, state=state
        )
    else:
        await message_generate(
            step_name='min_value_valid_error', message=message, state=state
        )


@edit_parameters_router.message(
    EditSearchParametersData.max_square
)
async def get_max_square(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with min_squere
    save min squere to data
    and send a request for max squere.
    """
    data = await state.get_data()
    if await max_value_validation_error(
        value=message.text,
        min_value=data['min_square']
    ):
        await message.delete()
        await state.update_data(max_square=message.text)

        await update_data_in_api(message=message, state=state)

        await state.clear()

        await message_generate(
            step_name='continue_edit_or_search',
            message=message
        )
    else:
        await message_generate(
            step_name='max_value_valid_error', message=message, state=state
        )


@edit_parameters_router.message(
    EditSearchParametersData.min_price
)
async def get_min_price(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with min price
    save min price to data
    and send a request for max price.
    """
    # await previous_bot_message_delete(
    #     previous_bot_message='min_price_question',
    #     state=state
    # )
    if (lambda value: value.isdigit() and (
            int(value) < 2147483647))(message.text):
        await message.delete()

        await state.update_data(min_price=message.text)

        await update_data_in_api(message=message, state=state)

        await state.clear()

        await message_generate(
            step_name='continue_edit_or_search',
            message=message
        )
    else:
        await message_generate(
            step_name='min_value_valid_error', message=message, state=state
        )


@edit_parameters_router.message(
    EditSearchParametersData.max_price
)
async def get_max_price(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with max price
    save max price to data
    and print all sender`s data like a message.
    """
    data = await state.get_data()
    if await max_value_validation_error(
        value=message.text,
        min_value=data['min_price']
    ):
        await message.delete()

        await state.update_data(max_price=message.text)

        await update_data_in_api(message=message, state=state)

        await state.clear()

        await message_generate(
            step_name='continue_edit_or_search',
            message=message
        )
    else:
        await message_generate(
            step_name='max_value_valid_error', message=message, state=state
        )
