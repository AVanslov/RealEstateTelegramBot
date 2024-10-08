import logging

from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from api_requests import (
    GET_OR_CREATE_USER,
    make_request,
) 
from messages import message_generate
# import keyboards as kb
# from constants import (
#     LANGUAGES,
# )
from states import SerachParametersData

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.set_state(SerachParametersData.language)

    telegram_id = message.from_user.id

    # пробуем получить объект Customer с текущим id
    # если получается
    # получаем язык этого пользователя
    # устанавливаем в состояние значение для языка
    # сразу спрашиваем первую букву города прямо в этом хендлере
    response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    logging.debug(
        f'Attempt to find user by telegram_id: {telegram_id} in DB'
        f'ended with a code: {response.status}.'
    )
    if response.status == 200:
        data = await response.json()
        language = data['language']
        logging.debug(
            'Language of current user is '
            f'{language}'
        )
        await state.update_data(language=language)
        await state.set_state(SerachParametersData.city_first_letter)
        await message_generate(
            step_name='city_first_letter', message=message, language=language
        )

    # если пользователь не найден
    # отправляем сообщение с вопросом о выборе языка
    # в следующем хендлере выполняем post запрос
    # с полученными параметрами пользователя
    else:
        await message_generate(step_name='start', message=message)
