# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
from miner.items import CPUItem, GPUItem, Product


class AlternateSpider(scrapy.Spider):
    name = "miner"
    allowed_domains = ["alternate.nl"]
    product_urls = {
        'cpu_listings': 'http://www.alternate.nl/html/product/listing.html'
                        '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
                        '=&size=500&bgid=10846&lk=9487&tk=7&navId=11572',
        'gpu_listings_nvidia': 'http://www.alternate.nl/html/product/listing.html'
                               '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
                               '=&size=500&bgid=11369&lk=9374&tk=7&navId=11606',
        'gpu_listings_ati': 'http://www.alternate.nl/html/product/listing.html'
                            '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
                            '=&size=500&bgid=10846&lk=9365&tk=7&navId=11608',
    }

    item_field = {
        'name': 'a[@class="productLink"]/span[@class="product"]/'
                'span[@class="description"]/h2/span[@class="name"]/'
                'span[2]/text()',
        'manufacturer': 'a[@class="productLink"]/span[@class="product"]/'
                        'span[@class="description"]/h2/span[@class="name"]/'
                        'span[1]/text()',
        'info_one': 'a[@class="productLink"]/span[@class="info"][1]/'
                    'text()',
        'info_two': 'a[@class="productLink"]/span[@class="info"][2]/'
                    'text()',
        'info_three': 'a[@class="productLink"]/span[@class="info"][3]/'
                      'text()',
        'price_big': 'div[@class="waresSum"]/p/span[@class="price right right10"]/'
                     'text()',
        'price_small': 'div[@class="waresSum"]/p/span[@class="price right right10"]/'
                       'sup/text()'
    }

    start_urls = list(product_urls.values())

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        rows = hxs.select('//div[@class="listRow"]')
        for row in rows:
            item = Product()
            item['manufacturer'] = row.select(self.item_field['manufacturer']).extract()
            item['name'] = row.select(self.item_field['name']).extract()
            item['price'] = row.select(self.item_field['price_big']).extract() + \
                            row.select(self.item_field['price_small']).extract()
            if response.url == self.product_urls['cpu_listings']:
                yield self.get_cpu(row, item)
            elif response.url == self.product_urls['gpu_listings_nvidia'] or \
                    response.url == self.product_urls['gpu_listings_ati']:
                yield self.get_gpu(row, item)

    def get_gpu(self, row, product):
        item = GPUItem()
        item['manufacturer'] = product['manufacturer']
        item['name'] = product['name']
        item['price'] = product['price']
        item['chipset'] = row.select(self.item_field['info_one']).extract()
        item['mem_type'] = row.select(self.item_field['info_two']).extract()
        item['mem_amount'] = row.select(self.item_field['info_two']).extract()
        item['slots'] = row.select(self.item_field['info_three']).extract()
        return item

    def get_cpu(self, row, product):
        item = CPUItem()
        item['manufacturer'] = product['manufacturer']
        item['name'] = product['name']
        item['price'] = product['price']
        item['speed'] = row.select(self.item_field['info_one']).extract()
        item['cores'] = row.select(self.item_field['info_two']).extract()
        item['socket'] = row.select(self.item_field['info_three']).extract()
        return item