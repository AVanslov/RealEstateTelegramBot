# For manual start-up use this command
# scrapy crawl cityexpert_belgrade -o cityexpert_belgrade.json
import scrapy
from scrapy.loader import ItemLoader

from ..items import RealEstateScraperItem


class CityexpertBelgradeSpider(scrapy.Spider):
    name = "cityexpert_belgrade"
    allowed_domains = ["cityexpert.rs"]
    start_urls = ["https://cityexpert.rs/prodaja-nekretnina/beograd"]
    custom_settings = {
        'FEEDS': {
            'cityexpert_belgrade.csv': {
                'format': 'csv'
            }
        }
    }

    def parse(self, response):
        pages = range(
            1, int(response.css('body > app > tui-root > tui-dropdown-host > div > main > search > div > div.serp-cards-map-wrap > div.serp-cards-wrap.toggle-list-map > cx-serp-results > div > div.serp-pagination-wrap-new.ng-star-inserted > div > ul > li:nth-child(3) > a::text').get())+1
        )
        for page in pages:
            url = response.urljoin('https://cityexpert.rs/prodaja-nekretnina/beograd' + '?currentPage={}'.format(page))
            yield scrapy.Request(
                url=url,
                callback=self.parse_page
            )

    def parse_page(self, response):
        for property_card in response.xpath("//app-property-card"):
            url = property_card.xpath(
                "./div/div[1]/div[1]/a/@href"
            ).get()
            property_type = property_card.xpath(
                './div/div[2]/div[1]/div[1]/div/div[2]/text()[2]'
            ).get()
            image_url = property_card.xpath(
                ".//img/@src"
            ).extract()

            yield scrapy.Request(
                url=url,
                callback=self.parse_item,
                cb_kwargs=dict(
                    property_type=property_type,
                    url=url,
                    image_url=image_url
                )

            )

    def parse_item(self, response, property_type, url, image_url):
        loader = ItemLoader(item=RealEstateScraperItem(), response=response)
        loader.add_css("title", "span.addressStreet")
        loader.add_css("description", "div.property-description > div > p")
        loader.add_value("property_type", property_type)
        loader.add_css("area", "div > prop-name-value:nth-child(5) > div > h5")
        loader.add_css("rooms_num", "div > div.prop-details > div:nth-child(1) > h5")
        loader.add_css("price", "div.price-type-wrap > h3 > span > span > span:nth-child(1)")
        loader.add_css("currency", "prop-price > div > div.price-type-wrap > h3 > span > span > span.eur-sym")
        loader.add_css("street_name", "span.addressStreet")
        loader.add_css("subdistrict_name", "span.addressRest > span.addressNbh.ng-star-inserted > a")
        loader.add_css("district_name", "span.addressRest > span.addressMncp > a")
        loader.add_css("city", "span.propId > span:nth-child(2)")
        loader.add_css("property_id", "span.propId > span.propIdNumber")
        loader.add_value("url", url)
        loader.add_value("image_url", image_url)
        return loader.load_item()
