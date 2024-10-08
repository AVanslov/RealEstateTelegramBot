import logging
import os
import sys
from threading import Timer
import json

from dotenv import load_dotenv
import pandas as pd
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from constants import FILES
from real_estate_scraper.spiders import (
    cityexpert_belgrade,
    halooglasi,
    zida
)
from validators import (
    additional_info_validator,
    area_validator,
    category_validator,
    city_validator,
    currency_validator,
    price_validator,
    rooms_number_validator,
    title_description_validator,
    url_image_url_validator,
)

logger = logging.getLogger(__name__)

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api/')

# API_BASE_URL = 'http://localhost:8000/api/'  # for local tests

DELETE_ALL_REALTIES = 'delete_all_realties/'
REALTIES = 'realty/'


def check_object(object: dict):
    object = {
        key: (value if str(value) != 'nan' else None) for key, value
        in object.items()
    }
    category = 'Apartment'
    rooms_number = False
    city = False
    url = False
    image_url = False

    if 'property_type' in object.keys() and (
        object['property_type'] is not None
    ):
        category = category_validator(value=object['property_type'])
    if 'rooms_num' in object.keys() and object['rooms_num'] is not None:
        rooms_number = rooms_number_validator(value=object['rooms_num'])
    if object['city'] and object['city'] is not None:
        city = city_validator(value=object['city'])
    if object['url'] and object['url'] is not None:
        url = url_image_url_validator(value=object['url'])
    if object['image_url'] and object['image_url'] is not None:
        image_url = url_image_url_validator(value=object['image_url'])

    if city and category and rooms_number and url and image_url:
        object = {
            "category": category,
            "city": city,
            "currency": currency_validator(object['currency']),
            "additional_info": additional_info_validator(object),
            "title": title_description_validator(
                field_name='title',
                value=object['title']
            ),
            "description": title_description_validator(
                field_name='description',
                value=object['description']
            ),
            "price": price_validator(object['price']),
            "area": area_validator(object['area']),
            "rooms_number": rooms_number,
            "image_url": image_url,
            "url": url
        }
        logging.debug(object)
        return object
    return False


def validate_csv_file(csv_file):
    with pd.read_csv(
        csv_file, chunksize=1000
    ) as reader:
        for chunk in reader:
            data_for_send = []
            for record in chunk.to_dict(orient="records"):
                validated_object = check_object(object=record)
                if validated_object:
                    data_for_send.append(validated_object)
                    logging.debug(
                        'Object has been validated and '
                        f'successefully added {validated_object}'
                    )

            yield data_for_send


def import_data(file_name):
    """
    Send POST request with list of data.
    """

    url = API_BASE_URL + REALTIES
    headers = {'Content-Type': 'application/json'}
    validated_data = validate_csv_file(csv_file=file_name)
    logging.debug('Start slice validated data')
    for validated_data_chank in validated_data:
        response = requests.post(
            url=url,
            json=validated_data_chank,
            headers=headers,
        )

        logging.debug(
            'Request has been sent with '
            f'response status code {response.status_code} '
            f'Data: {response.json()}'
            f'validated_data_chank: {validated_data_chank[:1]}'
        )


def delete_old_data():
    url = API_BASE_URL + REALTIES + DELETE_ALL_REALTIES
    response = requests.delete(url=url)
    return response


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    for file in FILES:
        if os.path.exists(file):
            os.remove(file)
        else:
            logging.debug(f'The file {file} does not exist')

    process.crawl(cityexpert_belgrade.CityexpertBelgradeSpider)
    process.crawl(halooglasi.HalooglasiSpider)
    process.crawl(zida.ZidaSpider)
    process.start()

    try:
        response = delete_old_data()
        if response.status_code == 204:
            logging.info(
                'Old data has been deleted succefully. '
                f'Status code is {response.status_code}'
            )
        else:
            logging.debug(
                'There are no data to delete yet.'
            )
    except ConnectionError:
        logging.debug('An attempt to delete old objects failed.')

    for file in FILES:
        try:
            logging.info(f'Start import data from file {file}.')
            import_data(file_name=file)
        except TypeError as e:
            logging.debug(e)
        except ValueError as e:
            logging.debug(e)
        except ConnectionError as e:
            logging.debug(e)
        except Exception as e:
            logging.debug(e)

    Timer(24 * 60 * 60, main).start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            # logging.FileHandler(filename=__file__ + '.log'),
            logging.StreamHandler(stream=sys.stdout),
        ],
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    )
    main()
