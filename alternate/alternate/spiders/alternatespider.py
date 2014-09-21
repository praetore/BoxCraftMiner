# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
from alternate.items import CPUItem


class AlternatespiderSpider(scrapy.Spider):
    name = "alternate"
    allowed_domains = ["alternate.nl"]
    start_urls = (
        'http://www.alternate.nl/html/product/listing.html?filter_5=&filter_4=&filter_3=&filter_2=&filter_1=&size=500&bgid=10846&lk=9487&tk=7&navId=11572#listingResult',
    )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        rows = hxs.select('//div[@class="listRow"]')
        for row in rows:
            item = CPUItem()
            item['manufacturer'] = row.select('a[@class="productLink"]/span[@class="product"]/'
                                              'span[@class="description"]/h2/span[@class="name"]/'
                                              'span[1]/text()').extract()
            item['name'] = row.select('a[@class="productLink"]/span[@class="product"]/'
                                      'span[@class="description"]/h2/span[@class="name"]/'
                                      'span[2]/text()').extract()
            item['socket'] = row.select('a[@class="productLink"]/span[@class="info"][3]/'
                                        'text()').extract()
            item['speed'] = row.select('a[@class="productLink"]/span[@class="info"][1]/'
                                       'text()').extract()
            item['cores'] = row.select('a[@class="productLink"]/span[@class="info"][2]/'
                                       'text()').extract()
            item['price'] = row.select('div[@class="waresSum"]/p/span[@class="price right right10"]/'
                                       'text()').extract() + row.select(
                                        'div[@class="waresSum"]/p/span[@class="price right right10"]/'
                                        'sup/text()').extract()
            yield item
