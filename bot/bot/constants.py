import numpy as np

from api_requests import GET_CATEGORIES, GET_CITIES, make_request
from settings import DEBAG

CITIES = [
    "Ada",
    "Aleksinac",
    "Apatin",
    "Arilje",
    "Avala",
    "Backa Topola",
    "Backi Jarak",
    "Backi Petrovac",
    "Backo Gradiste",
    "Banatsko Novo Selo",
    "Barajevo",
    "Basaid",
    "Batajnica",
    "Becej",
    "Belgrade",
    "Bocar",
    "Bor",
    "Cantavir",
    "Coka",
    "Cukarica",
    "Cuprija",
    "Debeljaca",
    "Despotovac",
    "Dolovo",
    "Drenovac",
    "Futog",
    "Glozan",
    "Golubinci",
    "Gornji Milanovac",
    "Grocka",
    "Ingija",
    "Izvor",
    "Jagodina",
    "Kacarevo",
    "Kanjiza",
    "Kovin",
    "Kragujevac",
    "Kraljevo",
    "Leskovac",
    "Loznica",
    "Melenci",
    "Nikinci",
    "Nova Pazova",
    "Novi Banovci",
    "Novi Becej",
    "Novi Belgrade",
    "Novi Pazar",
    "Novi Sad",
    "Odzaci",
    "Palic",
    "Paracin",
    "Petrovac",
    "Petrovaradin",
    "Pirot",
    "Popovac",
    "Priboj",
    "Prokuplje",
    "Ratkovo",
    "Ruma",
    "Rumenka",
    "Savski Venac",
    "Selo Mladenovac",
    "Senta",
    "Sibac",
    "Simanovci",
    "Sirig",
    "Smederevo",
    "Sombor",
    "Srbobran",
    "Sremcica",
    "Sremska Kamenica",
    "Sremska Mitrovica",
    "Sremski Karlovci",
    "Stara Pazova",
    "Stari Banovci",
    "Subotica",
    "Surcin",
    "Svilajnac",
    "Svrljig",
    "Temerin",
    "Titel",
    "Tornjos",
    "Ugrinovci",
    "Umcari",
    "Umka",
    "Vajska",
    "Valjevo",
    "Veternik",
    "Vrbas",
    "Zajecar",
    "Zemun Polje",
    "Zlatibor",
    "Zrenjanin"
]


async def get_cities():
    if DEBAG is True:
        cities = [i for i in CITIES]
    else:
        cities = await make_request(
            path=GET_CITIES,
            method='GET_LIST',
        )
        cities = [
            i['name'] for i in cities
        ]
        return cities

# получим все первые буквы, исключим дублирование букв
# и выстроим их в алфавитном порядке
ALPHABET_EN = sorted(list(set(sorted(
    [i[:1] for i in CITIES]
))))
ALPHABET_RU = ALPHABET_EN  # используем названия городов в оригинале


async def get_alphabet():
    if DEBAG:
        return sorted(list(set(sorted(
            [i[:1] for i in CITIES]
        ))))
    else:
        cities = await get_cities()
        return sorted(list(set(sorted(
            [i[:1] for i in cities]
        ))))


BACK = {
    'RU': ['Назад'],
    'EN': ['Back']
}
LANGUAGES = {
    'English 🇬🇧': 'EN',
    'Русский 🇷🇺': 'RU'
}
PROPERTY_TYPES = {
    'RU': [
        'Апартаменты',
        'Дом',
        'Апартаменты в доме',
    ],
    'EN': [
        'Apartment',
        'House',
        'Apartment in house',
    ]
}


async def get_property_types():
    if DEBAG:
        return PROPERTY_TYPES
    else:
        categories = await make_request(
            path=GET_CATEGORIES,
            method='GET_LIST',
        )
        property_types = {}
        en = [
            i['name'] for i in categories
        ]
        property_types['RU'] = en
        property_types['EN'] = en
        return property_types

NUMBER_OF_ROOMS = [str(i) for i in np.arange(1, 5, 0.5)]

SEARCH_OR_EDIT = {
    'RU': [
        'Поиск',
        'Редактировать параметры поиска'
    ],
    'EN': [
        'Search',
        'Edit search parameters'
    ]
}
SEARCH_PARAMETERS = {
    'City': 'city',
    'Property type': 'category',
    'Number of rooms': 'rooms_number',
    'Min square': 'min_area',
    'Max square': 'max_area',
    'Min price': 'min_price',
    'Max price': 'max_price',
}
