import logging

from aiogram import html
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from api_requests import GET_ALL_REALTIES, GET_CITIES, GET_OR_CREATE_SEARCH_PARAMETER, GET_OR_CREATE_USER, make_request
from constants import (
    LANGUAGES,
    NUMBER_OF_ROOMS,
    SEARCH_OR_EDIT,
    SEARCH_PARAMETERS,
    get_alphabet,
    get_cities,
    get_property_types,
)
import keyboards as kb
from serializers import DATA, REAL_ESTATES_DATA
from settings import DEBAG
from states import EditSearchParametersData


def all_search_parameters_message(data, language):
    if language == 'RU':
        message = (
            f'<b>Город:</b> {data["city"]};\n'
            f'<b>Тип недвижимости:</b> {data["category"]};\n'
            f'<b>Количество комнат:</b> {data["rooms_number"]};\n'
            f'<b>Минимально допустимая площадь:</b> {data["min_area"]};\n'
            f'<b>Максимально допустимая площадь:</b> {data["max_area"]};\n'
            f'<b>Минимальная стоимость в евро:</b> {data["min_price"]};\n'
            f'<b>Максимальная стоимость в евро:</b> {data["max_price"]}.\n'
        )
    else:
        message = (
            f'<b>City:</b> {data["city"]};\n'
            f'<b>Type of property:</b> {data["category"]};\n'
            f'<b>Number of rooms:</b> {data["rooms_number"]};\n'
            f'<b>Minimum allowed area:</b> {data["min_area"]};\n'
            f'<b>Maximum allowed area:</b> {data["max_area"]};\n'
            f'<b>Minimum cost in euros:</b> {data["min_price"]};\n'
            f'<b>The maximum cost in euros:</b> {data["max_price"]}.\n'
        )
    return message


async def start_message(message):
    """Return the message for start step."""
    await message.answer(
        f'Здравствуйте, {html.bold(message.from_user.full_name)}!\n'
        'Спешим сообщить, что вы всего в паре шагов от\n'
        'знакомства с вашей будущей недвижимостью.\n'
        '\n'
        'Пожалуйста, выберите язык, чтобы начать поиск.\n'
        '\n'
        f'Hello, {html.bold(message.from_user.full_name)}!\n'
        'We are glad to inform you that you are'
        'just a couple of steps away from '
        'getting to know your future real estate.\n'
        '\n'
        'Please select a language to start the search.',
        reply_markup=await kb.make_inline_keyboard(
            data_with_callback=LANGUAGES, raws=2
        )
    )


async def city_first_letter(
    language: str,
    callback: CallbackQuery = None,
    message: Message = None,
):
    """
    Return the messages and buttons for
    choose first letter of city name step.
    """

    ru_message = (
        '<b>Ура!</b>\nВы находитесь всего в нескольких шагах'
        'от дома вашей мечты.\n'
        'Пожалуйста, выберите первую букву города, '
        'в котором вы ищите недвижимость.'
    )
    en_message = (
        '<b>Hurray!</b>\nYou are just a few steps away from the property '
        'of your dreams.\n'
        'Please select the first letter of the city in '
        'which you are looking for real estate.'
    )

    ALPHABET_EN = await get_alphabet()

    if language == 'RU':
        if message is not None:
            await message.answer(
                ru_message,
                reply_markup=await kb.make_inline_keyboard(ALPHABET_EN, 4)
            )
        else:
            await callback.answer(
                ru_message
            )
            await callback.message.answer(
                ru_message,
                reply_markup=await kb.make_inline_keyboard(ALPHABET_EN, 4)
            )
    else:
        if message is not None:
            await message.answer(
                en_message,
                reply_markup=await kb.make_inline_keyboard(ALPHABET_EN, 4)
            )
        else:
            await callback.answer(
                en_message
            )
            await callback.message.answer(
                en_message,
                reply_markup=await kb.make_inline_keyboard(ALPHABET_EN, 4)
            )


async def city(callback, state):
    """
    Return the messages and buttons for
    choose city name step.
    """
    data = await state.get_data()
    ru_message = 'Пожалуйста, выберите город.'
    en_message = 'Please select a city.'

    if data['language'] == 'RU':
        await callback.answer(
            ru_message
        )
        await callback.message.answer(
            ru_message,
            reply_markup=await kb.cities(data['city_first_letter'])
        )
    else:
        await callback.answer(
            en_message
        )
        await callback.message.answer(
            en_message,
            reply_markup=await kb.cities(data['city_first_letter'])
        )


async def property_type(callback, state):
    """
    Return the messages and buttons for
    choose property_type step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        '\n'
        'Пожалуйста, выберите тип недвижимости.'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        '\n'
        'Please select the type of property.'
    )

    PROPERTY_TYPES = await get_property_types()

    if data['language'] == 'RU':
        await callback.answer(
            ru_message
        )
        await callback.message.answer(
            ru_message,
            reply_markup=await kb.make_inline_keyboard(PROPERTY_TYPES['RU'], 1)
        )
    else:
        await callback.answer(
            en_message
        )
        await callback.message.answer(
            en_message,
            reply_markup=await kb.make_inline_keyboard(PROPERTY_TYPES['EN'], 1)
        )


async def number_of_rooms(callback, state):
    """
    Return the messages and buttons for
    choose number_of_rooms step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        '\n'
        'Пожалуйста, выберите количество комнат.'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        '\n'
        'Please select the number of rooms.'
    )
    if data['language'] == 'RU':
        await callback.answer(
            ru_message
        )
        await callback.message.answer(
            ru_message,
            reply_markup=await kb.make_inline_keyboard(NUMBER_OF_ROOMS, 2)
        )
    else:
        await callback.answer(
            en_message
        )
        await callback.message.answer(
            en_message,
            reply_markup=await kb.make_inline_keyboard(NUMBER_OF_ROOMS, 2)
        )


async def min_square(callback: CallbackQuery, state: FSMContext):
    """
    Return the messages and buttons for
    choose min_square step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        '\n'
        'Пожалуйста, укажите минимально допустимую площадь в м2.\n'
        'Например так: 65'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        '\n'
        'Please specify the minimum allowed area in m2.\n'
        'For example: 65'
    )
    if data['language'] == 'RU':
        await callback.answer(
            ru_message
        )
        bot_message = await callback.message.answer(
            ru_message
        )
        return bot_message
    else:
        await callback.answer(
            en_message
        )
        bot_message = await callback.message.answer(
            en_message
        )
        # возврат (return) нужен для того, чтобы записывать данные об этом
        # сообщении в состояние,
        # а после удалять.
        # Сейчас этот функционал закомментирован - есть ошибка
        return bot_message


async def max_square(message: Message, state: FSMContext):
    """
    Return the messages and buttons for
    choose max_square step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        '\n'
        'Пожалуйста, укажите максимально допустимую площадь в м2.\n'
        'Например так: 105'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        '\n'
        'Please specify the maximum allowed area in m2.\n'
        'For example: 105'
    )
    if data['language'] == 'RU':
        bot_message = await message.answer(
            ru_message
        )
        return bot_message
    else:
        bot_message = await message.answer(
            en_message
        )
    return bot_message


async def min_price(message: Message, state: FSMContext):
    """
    Return the messages and buttons for
    choose min_price step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        f'<b>Максимально допустимая площадь:</b> {data["max_square"]};\n'
        '\n'
        'Пожалуйста, укажите минимально допустимую стоимость в евро.\n'
        'Например так: 6 500 000'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        f'<b>Maximum allowed area:</b> {data["max_square"]};\n'
        '\n'
        'Please specify the minimum allowable cost in Euro.\n'
        'For example: 6 500 000'
    )
    if data['language'] == 'RU':
        bot_message = await message.answer(
            ru_message
        )
        return bot_message
    else:
        bot_message = await message.answer(
            en_message
        )
    return bot_message


async def max_price(message: Message, state: FSMContext):
    """
    Return the messages and buttons for
    choose max_price step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        f'<b>Максимально допустимая площадь:</b> {data["max_square"]};\n'
        f'<b>Минимальная стоимость в евро:</b> {data["min_price"]};\n'
        '\n'
        'Пожалуйста, укажите максимально допустимую стоимость в евро.\n'
        'Например так: 6 500 000'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        f'<b>Maximum allowed area:</b> {data["max_square"]};\n'
        f'<b>Minimum cost in euros:</b> {data["min_price"]};\n'
        '\n'
        'Please specify the maximum allowable cost in Euro.\n'
        'For example: 6 500 000'
    )
    if data['language'] == 'RU':
        bot_message = await message.answer(
            ru_message,
            # reply_markup=await kb.make_inline_keyboard(
            #     BACK['RU'], 1
            # )
        )
        return bot_message
    else:
        bot_message = await message.answer(
            en_message,
            # reply_markup=await kb.make_inline_keyboard(
            #     BACK['EN'], 1
            # )
        )
    return bot_message


async def search_parameters_check(message: Message, state: FSMContext):
    """
    Return the messages and buttons for
    choose search_parameters_check step.
    """
    data = await state.get_data()
    ru_message = (
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        f'<b>Максимально допустимая площадь:</b> {data["max_square"]};\n'
        f'<b>Минимальная стоимость в евро:</b> {data["min_price"]};\n'
        f'<b>Максимальная стоимость в евро:</b> {data["max_price"]}.\n'
    )
    en_message = (
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        f'<b>Maximum allowed area:</b> {data["max_square"]};\n'
        f'<b>Minimum cost in euros:</b> {data["min_price"]};\n'
        f'<b>The maximum cost in euros:</b> {data["max_price"]}.\n'
    )
    if data['language'] == 'RU':
        await message.answer(
            ru_message,
            reply_markup=await kb.make_inline_keyboard(
                SEARCH_OR_EDIT['RU'], 2
            )
        )
    else:
        await message.answer(
            en_message,
            reply_markup=await kb.make_inline_keyboard(
                SEARCH_OR_EDIT['EN'], 2
            )
        )


async def min_value_valid_error(message: Message, state: FSMContext):
    """
    Return the message if validation error
    is in min_square step.
    """
    data = await state.get_data()
    ru_message = (
        'Пожалуйста, введите только натуральное число.\n'
        '\n'
        'Вы видите это сообщение,\n'
        'потому что указали 0, отрицательные числа,'
        'буквенные или прочие символы.\n'
        'Или число больше 2147483647.'
    )
    en_message = (
        'Please enter only a natural number.\n'
        '\n'
        'You see this message,\n'
        'because you specified 0, negative numbers, '
        'alphabetic or other characters.\n'
        'Or value more than 2147483647.'
    )
    if data['language'] == 'RU':
        await message.answer(
            ru_message,
        )
    else:
        await message.answer(
            en_message,
        )


async def max_value_valid_error(message: Message, state: FSMContext):
    """
    Return the message if validation error
    is in max_square step.
    """
    data = await state.get_data()
    ru_message = (
        'Пожалуйста, введите только натуральное число.\n'
        '\n'
        'Оно должно быть не меньше минимальной площади,'
        'которую вы указали в предыдущем поле.\n'
        'Вы видите это сообщение,\n'
        'потому что указали 0, отрицательные числа,'
        'буквенные или прочие символы, или'
        'максимальное значение меньше минимального.'
        'Или число больше 2147483647.'
    )
    en_message = (
        'Please enter only a natural number.\n'
        '\n'
        'It must be at least the minimum area'
        'that you specified in the previous field.\n'
        'You see this message,\n'
        'because you specified 0, negative numbers, '
        'alphabetic or other characters, or'
        'the maximum value is less than the minimum.\n'
        'Or value more than 2147483647.'
    )
    if data['language'] == 'RU':
        await message.answer(
            ru_message,
        )
    else:
        await message.answer(
            en_message,
        )


async def select_field_for_edit(callback: CallbackQuery):
    """
    Return the messages and buttons for
    select field for edit step.
    """
    # получить id из callback
    # получить объект Customer -> его язык
    # получить объект SearchParameter
    telegram_id = callback.from_user.id

    user_response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    language = (await user_response.json())['language']

    search_parameters_response = (
        await make_request(
            path=GET_OR_CREATE_SEARCH_PARAMETER,
            telegram_id=telegram_id
        )
    )
    search_parameters = await search_parameters_response.json()

    ru_message_first = (
        'Пожалуйста, выберите пункт, который вы хотите изменить\n'
        'Текущие параметры поиска:\n'
    )
    ru_message_second = all_search_parameters_message(
        data=search_parameters,
        language=language
    )
    en_message_first = (
        'Please select the item you want to change\n'
        'Current search parameters:\n'
    )
    en_message_second = all_search_parameters_message(
        data=search_parameters,
        language=language
    )

    buttons = list(SEARCH_PARAMETERS.keys())

    if language == 'RU':
        buttons.append(SEARCH_OR_EDIT['RU'][0])
        await callback.answer(
            ru_message_first,
        )
        await callback.message.answer(
            ru_message_first+ru_message_second,
            reply_markup=await kb.make_inline_keyboard(
                buttons, 2
            )
        )
    else:
        buttons.append(SEARCH_OR_EDIT['EN'][0])
        await callback.answer(
            en_message_first,
        )
        await callback.message.answer(
            en_message_first+en_message_second,
            reply_markup=await kb.make_inline_keyboard(
                buttons, 2
            )
        )


async def show_results(callback: CallbackQuery):
    """
    Return the messages and buttons for
    show results step.
    """
    telegram_id = callback.from_user.id

    user_response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    language = (await user_response.json())['language']

    search_parameters_response = await make_request(
        path=GET_OR_CREATE_SEARCH_PARAMETER,
        telegram_id=telegram_id
    )
    # параметры поискового запроса
    search_parameters = await search_parameters_response.json()

    # данные, полученные в результате поиска
    # по данным поискового запроса
    if DEBAG is True:
        results = REAL_ESTATES_DATA
    else:
        realty_response = await make_request(
            path=GET_ALL_REALTIES,
            params={
                'category__name': search_parameters['category'],
                'city__name': search_parameters['city'],
                'price__lt': search_parameters['max_price'],
                'price__gt': search_parameters['min_price'],
                'area__lt': search_parameters['max_area'],
                'area__gt': search_parameters['min_area'],
            }
        )
        results = await realty_response.json()

    if results:
        ru_message_first = (
            'Посмотрим, что нашлось.'
        )
        ru_message_second = (
            'Найдено {} подходящих объявления\n'.format(len(results))
        )
        current_result_index = 0

        ru_message_third = ''
        en_message_third = ''

        if "city" in results[current_result_index].keys():
            ru_message_third += f'<b>Город</b>: {results[current_result_index]["city"]}\n'
            en_message_third += f'<b>City</b>: {results[current_result_index]["city"]}\n'
        if "title" in results[current_result_index].keys():
            ru_message_third += f'<b>Название</b>: {results[current_result_index]["title"]}\n'
            en_message_third += f'<b>Name</b>: {results[current_result_index]["title"]}\n'
        if "additional_info" in results[current_result_index].keys():
            ru_message_third += (
                '<b>Адрес</b>:'
                f'{results[current_result_index]["additional_info"]}\n'
            )
            en_message_third += (
                '<b>Address</b>: '
                f'{results[current_result_index]["additional_info"]}\n'
            )
        if "price" in results[current_result_index].keys():
            ru_message_third += f'<b>Цена</b>: {results[current_result_index]["price"]}\n'
            en_message_third += f'<b>Price</b>: {results[current_result_index]["price"]}\n'
        if "description" in results[current_result_index].keys():
            ru_message_third += f'<b>Описание</b>: {results[current_result_index]["description"]}\n'
            en_message_third += f'<b>Description</b>: {results[current_result_index]["description"]}\n'
        if "category" in results[current_result_index].keys():
            ru_message_third += f'<b>Тип</b>: {results[current_result_index]["category"]}\n'
            en_message_third += f'<b>Type</b>: {results[current_result_index]["category"]}\n'
        if "area" in results[current_result_index].keys():
            ru_message_third += f'<b>Площадь</b>: {results[current_result_index]["area"]}\n'
            en_message_third += f'<b>Area</b>: {results[current_result_index]["area"]}\n'
        if "rooms_number" in results[current_result_index].keys():
            ru_message_third += f'<b>Количество комнат</b>: {results[current_result_index]["rooms_number"]}\n'
            en_message_third += f'<b>Rooms number</b>: {results[current_result_index]["rooms_number"]}\n'
        if "price" in results[current_result_index].keys():
            ru_message_third += f'<b>Стоимость</b>: {results[current_result_index]["price"]} {results[current_result_index]["currency"]}\n'
            en_message_third += f'<b>price</b>: {results[current_result_index]["price"]} {results[current_result_index]["currency"]}\n'
        ru_message_third += f'<a href="{results[current_result_index]["url"]}">Написать продавцу</a>\n'
        en_message_third += f'<a href="{results[current_result_index]["url"]}">Write to the seller</a>\n'

        en_message_first = (
            'Let`s see what we found.'
        )
        en_message_second = (
            '{} suitable ads found\n'.format(len(results))
        )

        if language == 'RU':
            await callback.answer(
                ru_message_first[:10],
            )
            await callback.message.answer_photo(
                photo=f'{results[current_result_index]["image_url"]}',
                caption=ru_message_second+ru_message_third,
                reply_markup=await kb.make_inline_keyboard(
                    raws=3,
                    data_with_callback=await kb.make_inline_pagination_buttons(
                        results, current_result_index
                    )
                )
            )

        else:
            await callback.answer(
                en_message_first[:10]
            )
            await callback.message.answer_photo(
                photo=f'{results[current_result_index]["image_url"]}',
                caption=en_message_second+en_message_third,
                reply_markup=await kb.make_inline_keyboard(
                    raws=3,
                    data_with_callback=await kb.make_inline_pagination_buttons(
                        results, current_result_index
                    )
                )
            )
    else:
        ru_message_first = 'Подходящие объявления не найдены'
        en_message_first = 'No suitable ads were found'
        ru_button = []
        ru_button.append(SEARCH_OR_EDIT['RU'][1])
        en_button = []
        en_button.append(SEARCH_OR_EDIT['EN'][1])

        if language == 'RU':
            await callback.message.answer(
                ru_message_first,
                reply_markup=await kb.make_inline_keyboard(
                    ru_button, 1
                )
            )
        else:
            await callback.message.answer(
                en_message_first,
                reply_markup=await kb.make_inline_keyboard(
                    en_button, 1
                )
            )


async def pagination(callback: CallbackQuery):
    telegram_id = callback.from_user.id

    user_response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    language = (await user_response.json())['language']

    search_parameters_response = await make_request(
        path=GET_OR_CREATE_SEARCH_PARAMETER,
        telegram_id=telegram_id
    )
    # параметры поискового запроса
    search_parameters = await search_parameters_response.json()

    # данные, полученные в результате поиска
    # по данным поискового запроса
    if DEBAG is True:
        results = REAL_ESTATES_DATA
    else:
        realty_response = await make_request(
            path=GET_ALL_REALTIES,
            params={
                'category__name': search_parameters['category'],
                'city__name': search_parameters['city'],
                'price__lt': search_parameters['max_price'],
                'price__gt': search_parameters['min_price'],
                'area__lt': search_parameters['max_area'],
                'area__gt': search_parameters['min_area'],
            }
        )
        results = await realty_response.json()

    current_result_index = int(callback.data)

    ru_message = ''
    en_message = ''

    if "city" in results[current_result_index].keys():
        ru_message += f'<b>Город</b>: {results[current_result_index]["city"]}\n'
        en_message += f'<b>City</b>: {results[current_result_index]["city"]}\n'
    if "title" in results[current_result_index].keys():
        ru_message += f'<b>Название</b>: {results[current_result_index]["title"]}\n'
        en_message += f'<b>Name</b>: {results[current_result_index]["title"]}\n'
    if "additional_info" in results[current_result_index].keys():
        ru_message += (
            '<b>Адрес</b>:'
            f'{results[current_result_index]["additional_info"]}\n'
        )
        en_message += (
            '<b>Address</b>: '
            f'{results[current_result_index]["additional_info"]}\n'
        )
    if "price" in results[current_result_index].keys():
        ru_message += f'<b>Цена</b>: {results[current_result_index]["price"]}\n'
        en_message += f'<b>Price</b>: {results[current_result_index]["price"]}\n'
    if "description" in results[current_result_index].keys():
        ru_message += f'<b>Описание</b>: {results[current_result_index]["description"]}\n'
        en_message += f'<b>Description</b>: {results[current_result_index]["description"]}\n'
    if "category" in results[current_result_index].keys():
        ru_message += f'<b>Тип</b>: {results[current_result_index]["category"]}\n'
        en_message += f'<b>Type</b>: {results[current_result_index]["category"]}\n'
    if "area" in results[current_result_index].keys():
        ru_message += f'<b>Площадь</b>: {results[current_result_index]["area"]}\n'
        en_message += f'<b>Area</b>: {results[current_result_index]["area"]}\n'
    if "rooms_number" in results[current_result_index].keys():
        ru_message += f'<b>Количество комнат</b>: {results[current_result_index]["rooms_number"]}\n'
        en_message += f'<b>Rooms number</b>: {results[current_result_index]["rooms_number"]}\n'
    if "price" in results[current_result_index].keys():
        ru_message += f'<b>Стоимость</b>: {results[current_result_index]["price"]} {results[current_result_index]["currency"]}\n'
        en_message += f'<b>Price</b>: {results[current_result_index]["price"]} {results[current_result_index]["currency"]}\n'
    ru_message += f'<a href="{results[current_result_index]["url"]}">Написать продавцу</a>\n'
    en_message += f'<a href="{results[current_result_index]["url"]}">Write to the seller</a>\n'

    if language == 'RU':
        await callback.answer(
            ru_message[:10],
        )
        await callback.message.answer_photo(
            photo=f'{results[current_result_index]["image_url"]}',
            caption=ru_message,
            reply_markup=await kb.make_inline_keyboard(
                raws=3,
                data_with_callback=await kb.make_inline_pagination_buttons(
                    results, current_result_index
                )
            )
        )

    else:
        await callback.answer(
            en_message[:10],
        )

        await callback.message.answer_photo(
            photo=f'{results[current_result_index]["image_url"]}',
            caption=en_message,
            reply_markup=await kb.make_inline_keyboard(
                raws=3,
                data_with_callback=await kb.make_inline_pagination_buttons(
                    results, current_result_index
                )
            )
        )


async def edit_max_square(callback: CallbackQuery, state: FSMContext):
    """
    Return the messages and buttons for
    choose max_square step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        '\n'
        'Пожалуйста, укажите максимально допустимую площадь в м2.\n'
        'Например так: 105'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        '\n'
        'Please specify the maximum allowed area in m2.\n'
        'For example: 105'
    )
    if data['language'] == 'RU':
        await callback.answer(
            ru_message[:10]
        )
        bot_message = await callback.message.answer(
            ru_message,
        )
    else:
        await callback.answer(
            en_message[:10]
        )
        bot_message = await callback.message.answer(
            en_message,
        )


async def edit_min_price(callback: CallbackQuery, state: FSMContext):
    """
    Return the messages and buttons for
    choose min_price step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        f'<b>Максимально допустимая площадь:</b> {data["max_square"]};\n'
        '\n'
        'Пожалуйста, укажите минимально допустимую стоимость в евро.\n'
        'Например так: 6 500 000'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        f'<b>Maximum allowed area:</b> {data["max_square"]};\n'
        '\n'
        'Please specify the minimum allowable cost in Euro.\n'
        'For example: 6 500 000'
    )
    if data['language'] == 'RU':

        await callback.answer(
            ru_message[:10]
        )
        bot_message = await callback.message.answer(
            ru_message,
        )
    else:
        await callback.answer(
            en_message[:10]
        )
        bot_message = await callback.message.answer(
            en_message,
        )


async def edit_max_price(callback: CallbackQuery, state: FSMContext):
    """
    Return the messages and buttons for
    choose max_price step.
    """
    data = await state.get_data()
    ru_message = (
        'Текущие параметры поиска:\n'
        f'<b>Город:</b> {data["city"]};\n'
        f'<b>Тип недвижимости:</b> {data["property_type"]};\n'
        f'<b>Количество комнат:</b> {data["number_of_rooms"]};\n'
        f'<b>Минимально допустимая площадь:</b> {data["min_square"]};\n'
        f'<b>Максимально допустимая площадь:</b> {data["max_square"]};\n'
        f'<b>Минимальная стоимость в евро:</b> {data["min_price"]};\n'
        '\n'
        'Пожалуйста, укажите максимально допустимую стоимость в евро.\n'
        'Например так: 6 500 000'
    )
    en_message = (
        'Current search parameters:\n'
        f'<b>City:</b> {data["city"]};\n'
        f'<b>Type of property:</b> {data["property_type"]};\n'
        f'<b>Number of rooms:</b> {data["number_of_rooms"]};\n'
        f'<b>Minimum allowed area:</b> {data["min_square"]};\n'
        f'<b>Maximum allowed area:</b> {data["max_square"]};\n'
        f'<b>Minimum cost in euros:</b> {data["min_price"]};\n'
        '\n'
        'Please specify the maximum allowable cost in Euro.\n'
        'For example: 6 500 000'
    )
    if data['language'] == 'RU':
        await callback.answer(
            ru_message[:10]
        )
        bot_message = await callback.message.answer(
            ru_message,
        )
    else:
        await callback.answer(
            en_message[:10]
        )
        bot_message = await callback.message.answer(
            en_message,
        )


async def edit_selected_field(callback: CallbackQuery, state: FSMContext):
    """
    Return the messages and buttons for
    edit selected field step.
    """
    telegram_id = callback.from_user.id

    user_response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    language = (await user_response.json())['language']

    search_parameters_response = (
        await make_request(
            path=GET_OR_CREATE_SEARCH_PARAMETER,
            telegram_id=telegram_id
        )
    )
    search_parameters = await search_parameters_response.json()

    editable_item = callback.data
    ru_message_first = (
        f'Вы выбрали пункт {editable_item}'
    )
    ru_message_second = (
        f'Вы выбрали пункт {editable_item}\n'
        '<b>Старое значение:</b> '
        f'{search_parameters[SEARCH_PARAMETERS[editable_item]]}\n'
        'Пожалуйста, введите новое значение.'
    )
    en_message_first = (
        f'You have selected {editable_item}'
    )
    en_message_second = (
        f'You have selected {editable_item}\n'
        '<b>Old value:</b> '
        f'{search_parameters[SEARCH_PARAMETERS[editable_item]]}\n'
        'Please enter a new value.'
    )
    await state.update_data(language=language)
    await state.update_data(city=search_parameters['city'])
    await state.update_data(property_type=search_parameters['category'])
    await state.update_data(number_of_rooms=search_parameters['rooms_number'])
    await state.update_data(min_square=search_parameters['min_area'])
    await state.update_data(max_square=search_parameters['max_area'])
    await state.update_data(min_price=search_parameters['min_price'])
    await state.update_data(max_price=search_parameters['max_price'])

    ALPHABET_EN = await get_alphabet()

    if editable_item == 'City':
        await state.set_state(EditSearchParametersData.city_first_letter)
        ru_reply_markup = await kb.make_inline_keyboard(ALPHABET_EN, 4)
        en_reply_markup = await kb.make_inline_keyboard(ALPHABET_EN, 4)

        if language == 'RU':
            await callback.answer(
                ru_message_first
            )
            await callback.message.answer(
                ru_message_second,
                reply_markup=ru_reply_markup
            )
        else:
            await callback.answer(
                en_message_first,
            )
            await callback.message.answer(
                en_message_second,
                reply_markup=en_reply_markup
            )
    elif editable_item == 'Property type':
        await state.set_state(EditSearchParametersData.property_type)
        await message_generate(
            step_name='property_type',
            callback=callback,
            state=state
        )

    elif editable_item == 'Number of rooms':
        await state.set_state(EditSearchParametersData.number_of_rooms)
        await message_generate(
            step_name='number_of_rooms',
            callback=callback,
            state=state
        )

    elif editable_item == 'Min square':
        await state.set_state(EditSearchParametersData.min_square)
        await message_generate(
            step_name='min_square',
            callback=callback,
            state=state
        )

    elif editable_item == 'Max square':
        await state.set_state(EditSearchParametersData.max_square)
        await message_generate(
            step_name='edit_max_square',
            callback=callback,
            state=state
        )

    elif editable_item == 'Min price':
        await state.set_state(EditSearchParametersData.min_price)
        await message_generate(
            step_name='edit_min_price',
            callback=callback,
            state=state
        )

    elif editable_item == 'Max price':
        await state.set_state(EditSearchParametersData.max_price)
        await message_generate(
            step_name='edit_max_price',
            callback=callback,
            state=state
        )


async def continue_edit_or_search(
    callback: CallbackQuery = None,
    message: Message = None
):
    """
    Return the messages and buttons for
    choose continue_edit_or_search step.
    """
    if callback is not None:
        telegram_id = callback.from_user.id
    else:
        telegram_id = message.from_user.id

    user_response = await make_request(
        path=GET_OR_CREATE_USER,
        telegram_id=telegram_id
    )
    language = (await user_response.json())['language']

    search_parameters_response = (
        await make_request(
            path=GET_OR_CREATE_SEARCH_PARAMETER,
            telegram_id=telegram_id
        )
    )
    search_parameters = await search_parameters_response.json()

    messages = all_search_parameters_message(
        data=search_parameters,
        language=language
    )
    if message is None:
        if language == 'RU':
            await callback.answer(
                messages[:10]
            )
            await callback.message.answer(
                messages,
                reply_markup=await kb.make_inline_keyboard(
                    SEARCH_OR_EDIT['RU'], 2
                )
            )
        else:
            await callback.answer(
                messages[:10]
            )
            await callback.message.answer(
                messages,
                reply_markup=await kb.make_inline_keyboard(
                    SEARCH_OR_EDIT['EN'], 2
                )
            )
    else:
        if language == 'RU':
            await message.answer(
                messages,
                reply_markup=await kb.make_inline_keyboard(
                    SEARCH_OR_EDIT['RU'], 2
                )
            )
        else:
            await message.answer(
                messages,
                reply_markup=await kb.make_inline_keyboard(
                    SEARCH_OR_EDIT['EN'], 2
                )
            )


async def message_generate(
    step_name: str,
    message: Message = None,
    state: FSMContext = None,
    callback: CallbackQuery = None,
    language: str = None,
) -> None:
    """
    Returns the message,
    buttons, and answers
    in the selected language.
    """

    if step_name == 'start':
        await start_message(message)
    elif step_name == 'city_first_letter':
        await city_first_letter(
            message=message,
            callback=callback,
            language=language
        )
    elif step_name == 'city' or step_name == 'edit_city':
        await city(callback, state)

    elif step_name == 'property_type':
        await property_type(callback, state)
    elif step_name == 'number_of_rooms':
        await number_of_rooms(callback, state)
    elif step_name == 'min_square':
        await min_square(callback, state)
    elif step_name == 'max_square':
        await max_square(message, state)
    elif step_name == 'min_price':
        await min_price(message, state)
    elif step_name == 'max_price':
        await max_price(message, state)
    elif step_name == 'search_parameters_check':
        await search_parameters_check(message, state)
    elif step_name == 'min_value_valid_error':
        await min_value_valid_error(message, state)
    elif step_name == 'max_value_valid_error':
        await max_value_valid_error(message, state)
    elif step_name == 'select_field_for_edit':
        await select_field_for_edit(callback)
    elif step_name == 'edit_selected_field':
        await edit_selected_field(callback, state)
    elif step_name == 'show_results':
        await show_results(callback)
    elif step_name == 'pagination':
        await pagination(callback)

    elif step_name == 'continue_edit_or_search':
        await continue_edit_or_search(callback, message)
    elif step_name == 'edit_max_square':
        await edit_max_square(callback, state)
    elif step_name == 'edit_min_price':
        await edit_min_price(callback, state)
    elif step_name == 'edit_max_price':
        await edit_max_price(callback, state)
    else:
        raise Exception('The program is trying to show an unknown message.')
