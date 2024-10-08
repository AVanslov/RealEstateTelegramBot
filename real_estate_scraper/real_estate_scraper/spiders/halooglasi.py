import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader

from real_estate_scraper.items import RealEstateScraperItem


# class HalooglasiSpider(CrawlSpider):
#     name = "halooglasi"
#     allowed_domains = ["halooglasi.com"]
#     start_urls = ["https://www.halooglasi.com/nekretnine/prodaja-stanova"]

#     rules = (
#         Rule(LinkExtractor(allow=(r"page=",))),
#         Rule(LinkExtractor(
#             restrict_css='h3.product-title a'
#         ), callback='parse_item')),
#     )

#     def parse_item(self, response):
#         l = ItemLoader(item=HalooglasiParserItem(), response=response)
#         l.add_css("title", "#plh1")
#         l.add_css("description", "#plh50")
#         l.add_css("city", "#plh2")
#         l.add_css("district_name", "#plh3")
#         l.add_css("subdistrict_name", "#plh4")
#         l.add_css("street_name", "#plh5")
#         ...
#         return l.load_item()


class HalooglasiSpider(scrapy.Spider):
    """Паук для сбора данных с https://www.halooglasi.com/."""

    name = "halooglasi"
    allowed_domains = ["halooglasi.com"]
    start_urls = ["https://www.halooglasi.com/nekretnine/prodaja-stanova"]
    custom_settings = {
        "FEEDS": {
            "halooglasi.csv": {
                "format": "csv"
            }
        }
    }

    def parse(self, response: Response):
        page = 1
        url = response.urljoin(
            "https://www.halooglasi.com/nekretnine/prodaja-stanova"
            + f"?page={page}"
        )
        yield scrapy.Request(
            url=url,
            callback=self.parse_page,
            meta={"page": page},
            dont_filter=True
        )

    def parse_page(self, response: Response):
        items = response.css(
            "div.widget-ad-list > div.row.product-list > div.col-md-12:not(.banner-list-item)"
        )

        if not items:
            self.logger.info(
                f"No items found on page {response.meta['page']}, stopping pagination."
            )
            return

        for item in items:
            yield self.parse_item(response, item)

        next_page = response.meta["page"] + 1
        next_url = response.urljoin(
            f"https://www.halooglasi.com/nekretnine/prodaja-stanova?page={next_page}"
        )
        yield scrapy.Request(
            url=next_url,
            callback=self.parse_page,
            meta={"page": next_page},
            dont_filter=True
        )

    def parse_item(self, response, item):
        loader = ItemLoader(item=RealEstateScraperItem(), selector=item)

        loader.add_css("title", "h3.product-title > a::text")
        loader.add_css("description", "p.text-description-list::text")

        area = None
        rooms = None

        for feature in item.css("ul.product-features > li > div"):
            label = feature.css("span::text").get()
            value = feature.css("::text").get()

            if label == "Kvadratura" and value:
                area = value.replace("m", "").strip()
            elif label == "Broj soba" and value:
                rooms = value.strip()

        if area:
            loader.add_value("area", area)
        if rooms:
            loader.add_value("rooms_num", rooms)

        price_text = item.css("div.central-feature > span > i::text").get()
        if price_text:
            price_cleaned = price_text.strip().replace('€', '').strip()
            currency = '€'  # Предполагается, что валюта всегда евро
            loader.add_value("currency", currency)
            loader.add_value("price", price_cleaned)

        address_parts = item.css("ul.subtitle-places > li::text").getall()
        if len(address_parts) >= 4:
            city = address_parts[0].strip()
            district_name = address_parts[1].strip()
            subdistrict_name = address_parts[2].strip()
            street_name = address_parts[3].strip()

            loader.add_value("city", city)
            loader.add_value("district_name", district_name)
            loader.add_value("subdistrict_name", subdistrict_name)
            loader.add_value("street_name", street_name)

        relative_url = item.css("h3.product-title > a::attr(href)").get()
        absolute_url = response.urljoin(relative_url)
        loader.add_value("url", absolute_url)

        loader.add_css("image_url", "div.col-md-4 > figure.pi-img-wrapper > a.a-images > img::attr(src)")

        return loader.load_item()
