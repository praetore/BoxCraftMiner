# -*- coding: utf-8 -*-
import re
from urlparse import urlparse
import scrapy
from miner.items import CPUItem, GPUItem, Product, MemoryItem, MainboardItem


listings = {
    'motherboard': 'http://www.computerstore.nl/category/208882/moederborden.html?items=100',
    'cpu': 'http://www.computerstore.nl/category/208406/processoren.html?items=100',
    'gpu': 'http://www.computerstore.nl/category/200657/computergeheugen.html?items=100',
    'memory': 'http://www.computerstore.nl/category/202958/videokaarten.html?items=100'
}

class ComputerstoreSpider(scrapy.Spider):
    name = "computerstore"
    allowed_domains = ["computerstore.nl"]
    start_urls = (i for i in listings.values())

    def parse(self, response):
        rows = response.xpath('//li[@class="product-list-columns--item product-list-item"]')
        for row in rows:
            desc = row.xpath('h4/a/text()').extract()[0]
            desc_groups = re.match(r'^(\w+) ([\w ]+)$', desc)
            if desc_groups:
                item = Product()
                if desc_groups.group(1) != 'Club':
                    item['manufacturer'] = desc_groups.group(1)
                    item['name'] = desc_groups.group(2)
                else:
                    item['manufacturer'] = 'Club 3D'
                    item['name'] = desc_groups.group(2).replace('3D', '')
                item['price'] = row.xpath('//strong[@class="product-list-item--price"]/text()').extract()[0]
                parse_url = urlparse(response.url)
                link = parse_url.scheme + '://' + parse_url.netloc + row.xpath('h4/a/@href').extract()[0]
                category = listings.keys()[listings.values().index(response.url)]
                print 'Category %s' % category
                request = scrapy.Request(link, callback='get_%s' % category)
                request.meta['item'] = item
                return request
            else:
                return None

    def get_motherboard(self, response):
        item = response.meta['item']
        yield item

    def get_gpu(self, response):
        item = response.meta['item']
        yield item

    def get_cpu(self, response):
        item = response.meta['item']
        yield item

    def get_memory(self, response):
        item = response.meta['item']
        yield item