import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def clean_data(value):
    chars_to_remove = ["_", "\\", "\n", "m²"]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    return value.strip()


def remove_dote(value):
    chars_to_remove = ["."]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    return value.strip()


class RealEstateScraperItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    property_type = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    area = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    rooms_num = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data, remove_dote),
        output_processor=TakeFirst(),
    )
    currency = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    street_name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    subdistrict_name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    district_name = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    city = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    property_id = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_data),
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
    image_url = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=TakeFirst(),
    )
