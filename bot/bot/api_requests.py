import aiohttp
import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api/')

GET_OR_CREATE_USER = 'user/'
GET_ALL_REALTIES = 'realty/'
GET_OR_CREATE_SEARCH_PARAMETER = 'search_parameter/'
GET_CITIES = 'city/'
GET_CATEGORIES = 'category/'


async def make_request(
    path: str,
    method: str = 'GET',
    json: dict | None = None,
    telegram_id=None,
    params: dict | None = None
):
    async with aiohttp.ClientSession() as session:
        if telegram_id is not None:
            full_path = API_BASE_URL + path + str(telegram_id) + '/'
        else:
            full_path = API_BASE_URL + path

        logging.debug(f'Full path is {full_path}')

        if method == 'POST':
            async with session.post(full_path, json=json) as response:
                logging.debug(response.status)
                logging.debug(await response.json())
                return response

        elif method == 'GET':
            async with session.get(full_path, params=params) as response:
                logging.debug(response.status)
                logging.debug(await response.json())
                return response

        elif method == 'GET_LIST':
            async with session.get(full_path) as response:
                logging.debug(response.status)
                logging.debug(await response.json())
                return await response.json()

    await session.close()
