import logging
import re

from constants import (
    CATEGORIES,
    CITIES,
    CURRENCIES,
    NO_DATA_MESSAGE,
    ROOMS_NUMBERS,
)


def category_validator(value) -> str | bool:
    """
    Check category value and return expected by API value.
    Or return False if value cannot be processed.
    """
    if isinstance(value, str) and (
        value in CATEGORIES.keys()
    ):
        return CATEGORIES[value]

    return False


def rooms_number_validator(value) -> float | bool:
    """
    Check rooms_number value and return expected by API value.
    Or return False if value cannot be processed.
    """
    values_for_replace = [' soba', '+']
    if isinstance(value, str):
        if value in ROOMS_NUMBERS.keys():
            return ROOMS_NUMBERS[value]
        else:
            for symbol in values_for_replace:
                value = value.replace(symbol, '')
            return float(value)
    elif isinstance(value, int) or isinstance(value, float):
        try:
            return float(value)
        except ValueError:
            logging.warning(f'Can`t convert {value} to float')
    return False


def city_validator(value) -> str | bool:
    """
    Check city value and return expected by API value.
    Or return False if value cannot be processed.
    """
    if isinstance(value, str) and (
        value in CITIES.keys()
    ):
        return CITIES[value]
    return False


def additional_info_validator(object):
    args = []
    if 'district_name' in object.keys():
        district_name = object['district_name']
        args.append(district_name)
    if 'subdistrict_name' in object.keys():
        subdistrict_name = object['subdistrict_name'],
        args.append(subdistrict_name)
    if 'street_name' in object.keys():
        street_name = object['street_name']
        args.append(street_name)

    if any(
        isinstance(value, str) and (
            len(value) > 0 and (
                bool(re.match(r'\w.\-', value))
            )
        ) for value in args
    ):
        return ', '.join([str(value) for value in args if args != 0])
    return NO_DATA_MESSAGE


def currency_validator(value):
    if value in CURRENCIES.keys():
        return CURRENCIES[value]
    return 'EUR'


def area_validator(value):
    if isinstance(value, int) or isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        value = value.replace(',', '.')
        return int(value)
    return 0


def price_validator(value):
    if isinstance(value, str):
        value = value.replace('.', '')
        if value.isdigit():
            return int(value)
    elif isinstance(value, int):
        return int(value)
    return 0


def title_description_validator(field_name, value):
    if field_name == 'title':
        max_value_length = 128
    max_value_length = 500

    if isinstance(value, str) and (
        bool(re.match(r'\w.\-', value))
    ):
        if len(value) > max_value_length:
            return value[:max_value_length] + '...'
        return value
    return NO_DATA_MESSAGE


def url_image_url_validator(value):
    if isinstance(value, str):
        return value
    return False
