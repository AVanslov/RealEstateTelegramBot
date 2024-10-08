import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader

from real_estate_scraper.items import RealEstateScraperItem


class ZidaSpider(scrapy.Spider):
    """Паук для сбора данных с https://www.4zida.rs/prodaja-stanova."""

    name = "zida"
    allowed_domains = ["4zida.rs"]
    start_urls = ["https://www.4zida.rs/prodaja-stanova"]
    custom_settings = {
        "FEEDS": {
            "zida.csv": {
                "format": "csv"
            }
        }
    }

    def parse(self, response: Response):
        page = 1
        yield from self.parse_page(response, page)

    def parse_page(self, response: Response, page: int):
        items = response.css("div[test-data='ad-search-card']")
        for item in items:
            yield self.parse_item(response, item)

        if page < 100:
            next_page_url = f"https://www.4zida.rs/prodaja-stanova?page={page + 1}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_page_with_page_number,
                meta={"page": page + 1},
                dont_filter=True
            )

    def parse_page_with_page_number(self, response: Response):
        # Получаем номер страницы из метаданных запроса
        page = response.meta.get('page', 1)
        yield from self.parse_page(response, page)

    def parse_item(self, response: Response, item):
        loader = ItemLoader(item=RealEstateScraperItem(), selector=item)

        loader.add_css("title", "div.flex > a.flex > div.w-5\\/8 p.truncate::text")
        area_info = item.css("div.flex > a.px-3::text").get()
        if area_info:
            area_info_parts = area_info.split('|')
            for part in area_info_parts:
                part = part.strip()
                if "m²" in part:
                    area_value = part.replace('m²', '').strip()
                    loader.add_value("area", area_value)
                elif "sobe" or "soba" in part:
                    if "sobe":
                        room_num_value = part.replace("sobe", "").strip()
                        loader.add_value("rooms_num", room_num_value)
                    else:
                        room_num_value = part.replace("soba", "").strip()
                        loader.add_value("rooms_num", room_num_value)

        address = item.css("div.flex > a.flex > div.w-5\\/8 > p.line-clamp-2::text").get()
        if address:
            address_parts = [part.strip() for part in address.split(',')]
            if len(address_parts) == 2:
                district_name, city = address_parts
                loader.add_value("city", city)
                loader.add_value("district_name", district_name)
            elif len(address_parts) == 3:
                # Предполагаем, что формат: [улица, подрайон, город]
                street_name, subdistrict_name, city = address_parts
                loader.add_value("city", city)
                loader.add_value("subdistrict_name", subdistrict_name)
                loader.add_value("street_name", street_name)
            elif len(address_parts) == 4:
                # Предполагаем, что формат: [улица, подрайон, район, город]
                street_name, subdistrict_name, district_name, city = address_parts
                loader.add_value("city", city)
                loader.add_value("district_name", district_name)
                loader.add_value("subdistrict_name", subdistrict_name)
                loader.add_value("street_name", street_name)

        price_text = item.css("div.flex > a.flex > div.w-3\\/8 > p.rounded-tl::text").get()
        if price_text:
            price_cleaned = price_text.strip().replace('€', '').strip()
            currency = "€"
            loader.add_value("currency", currency)
            loader.add_value("price", price_cleaned)

        relative_url = item.css("div.flex > a.flex::attr(href)").get()
        absolute_url = response.urljoin(relative_url)
        loader.add_value("url", absolute_url)

        loader.add_css("image_url", "div.relative > a > div.relative.size-full > img::attr(src)")

        return loader.load_item()
