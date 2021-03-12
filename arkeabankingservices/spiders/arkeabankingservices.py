import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from arkeabankingservices.items import Article


class ArkeabankingservicesSpider(scrapy.Spider):
    name = 'arkeabankingservices'
    start_urls = ['https://www.arkea-banking-services.com/outsourcing/externalisation/services-bancaires/tl_5315/en/our-news']

    def parse(self, response):
        links = response.xpath('//div[@class="article-picture col-md-4"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pgNext"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="article-pdate"]/text()').get()
        if date:
            date = " ".join(date.strip().split()[2:])

        content = response.xpath('//div[@class="article-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
