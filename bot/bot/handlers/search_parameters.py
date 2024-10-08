import logging

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from api_requests import (
    GET_ALL_REALTIES,
    GET_OR_CREATE_SEARCH_PARAMETER,
    GET_OR_CREATE_USER,
    make_request,
)
from constants import (
    BACK,
    LANGUAGES,
    NUMBER_OF_ROOMS,
    PROPERTY_TYPES,
    SEARCH_OR_EDIT,
)
from messages import message_generate
from serializers import DATA
from states import SerachParametersData
from validators import max_value_validation_error

search_parameters_router = Router()


async def previous_bot_message_delete(
    previous_bot_message: str,
    state: FSMContext
):
    """
    Delete a message from the previous handler.
    """
    data = await state.get_data()
    previous_message = data[previous_bot_message]
    # Удаляем сообщение от бота из предыдущего хендлера
    await previous_message.delete()


@search_parameters_router.callback_query(F.data.in_(set(LANGUAGES.values())))
async def search_parameters_city_first_letter(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    This handler recive callback data with language
    and the procedure for creating a state
    with information about the desired real
    estate objects begins.
    """
    language = callback.data

    await state.update_data(language=language)
    # запрос к API
    # в предыдущем хендлере мы проверили, что такого пользовтеля точно нет в БД
    # отправляем post запрос на создание пользователя
    telegram_id = callback.from_user.id
    logging.debug(f'Current user id: {telegram_id}')
    json = {
        'language': str(language),
        'telegram_id': int(telegram_id),
        'username': str(callback.from_user.username)
    }

    response = await make_request(
            method='POST',
            path=GET_OR_CREATE_USER,
            json=json
        )

    logging.debug(
        f'New user with id {telegram_id} '
        'has been seccussfully created.'
        f'Status code is {response.status}'
    )

    await callback.message.delete()
    await state.set_state(SerachParametersData.city_first_letter)
    await message_generate(
        step_name='city_first_letter', callback=callback, language=language
    )


@search_parameters_router.callback_query(
    SerachParametersData.city_first_letter
)
async def serach_parameters_city(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Show Inline buttons with Serbian Cities.
    """

    await state.update_data(city_first_letter=callback.data)
    await callback.message.delete()
    await state.set_state(SerachParametersData.city)
    await message_generate(
        step_name='city', callback=callback, state=state
    )


@search_parameters_router.callback_query(
    SerachParametersData.city
)
async def serach_parameters_property_type(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Show Inline buttons with property_types.
    """
    await state.update_data(city=callback.data)
    await callback.message.delete()
    await state.set_state(SerachParametersData.property_type)
    await message_generate(
        step_name='property_type', callback=callback, state=state
    )


@search_parameters_router.callback_query(
    SerachParametersData.property_type
)
async def serach_parameters_number_of_rooms(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Show Inline buttons with number of rooms.
    """
    await state.update_data(property_type=callback.data)
    await callback.message.delete()
    await state.set_state(SerachParametersData.number_of_rooms)
    await message_generate(
        step_name='number_of_rooms', callback=callback, state=state
    )


@search_parameters_router.callback_query(
    SerachParametersData.number_of_rooms
)
async def search_parameters_min_square(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    This handler recive a message with number_of_rooms
    save number_of_rooms to data
    and send a request for min_square.
    """

    await state.update_data(number_of_rooms=callback.data)
    await callback.message.delete()
    await state.set_state(SerachParametersData.min_square)

    bot_message = await message_generate(
        step_name='min_square', callback=callback, state=state
    )
    # записываем данные о сообщении в состояние,
    # чтобы в следущем хендлере удалить данное сообщение
    # await state.update_data(min_square_question=bot_message)


@search_parameters_router.message(
    SerachParametersData.min_square
)
async def search_parameters_max_square(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with min_squere
    save min squere to data
    and send a request for max squere.
    """
    # await previous_bot_message_delete(
    #     previous_bot_message='min_square_question',
    #     state=state
    # )
    if (lambda value: value.isdigit() and (
            int(value) < 2147483647))(message.text):
        await state.update_data(min_square=message.text)
        await message.delete()
        await state.set_state(SerachParametersData.max_square)
        await message_generate(
            step_name='max_square', message=message, state=state
        )
    else:
        await message_generate(
            step_name='min_value_valid_error', message=message, state=state
        )
    # await state.update_data(max_square_question=bot_message)


@search_parameters_router.message(
    SerachParametersData.max_square
)
async def serach_parameters_min_price(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with max_squere
    save max squere to data
    and send a request for min price.
    """

    # await previous_bot_message_delete(
    #     previous_bot_message='max_square_question',
    #     state=state
    # )
    data = await state.get_data()
    if await max_value_validation_error(
        value=message.text,
        min_value=data['min_square']
    ):
        await state.update_data(max_square=message.text)
        await message.delete()
        await state.set_state(SerachParametersData.min_price)
        await message_generate(
            step_name='min_price', message=message, state=state
        )
    else:
        await message_generate(
            step_name='max_value_valid_error', message=message, state=state
        )
    # await state.update_data(min_price_question=bot_message)


@search_parameters_router.message(
    SerachParametersData.min_price
)
async def serach_parameters_max_price(
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
        await state.update_data(min_price=message.text)
        await message.delete()
        await state.set_state(SerachParametersData.max_price)
        await message_generate(
            step_name='max_price', message=message, state=state
        )
    else:
        await message_generate(
            step_name='min_value_valid_error', message=message, state=state
        )

@search_parameters_router.message(
    SerachParametersData.max_price
)
async def search_parameters_check_data(
    message: Message, state: FSMContext
) -> None:
    """
    This handler recive a message with max price
    save max price to data
    and print all sender`s data like a message.
    """
    # await previous_bot_message_delete(
    #     previous_bot_message='max_price_question',
    #     state=state
    # )
    data = await state.get_data()
    if await max_value_validation_error(
        value=message.text,
        min_value=data['min_price']
    ):
        await state.update_data(max_price=message.text)
        await message.delete()
        await message_generate(
            step_name='search_parameters_check', message=message, state=state
        )
        # сохранение полученных данны в БД
        data = await state.get_data()
        telegram_id = message.from_user.id
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
            'Search parameter object has been created'
            f'by user with id {telegram_id}. '
            f'Response status code is {response.status}.'
        )
        await state.clear()
    else:
        await message_generate(
            step_name='max_value_valid_error', message=message, state=state
        )
