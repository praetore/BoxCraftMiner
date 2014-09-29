# -*- coding: utf-8 -*-
import re
from urlparse import urlparse
import scrapy
from scrapy.selector import HtmlXPathSelector
from miner.items import CPUItem, GPUItem, Product, MemoryItem, MainboardItem
from unidecode import unidecode


class AlternateSpider(scrapy.Spider):
    name = "alternate"
    allowed_domains = ["alternate.nl"]

    cpu_listings = ['http://www.alternate.nl/html/product/listing.html'
                    '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
                    '=&size=500&bgid=10846&lk=9487&tk=7&navId=11572']

    gpu_listings = {
        'nvidia': 'http://www.alternate.nl/html/product/listing.html'
                  '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
                  '=&size=500&bgid=11369&lk=9374&tk=7&navId=11606',
        'ati': 'http://www.alternate.nl/html/product/listing.html'
               '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1'
               '=&size=500&bgid=10846&lk=9365&tk=7&navId=11608'}

    memory_listings = {
        'ddr': 'http://www.alternate.nl/html/product/listing.html'
               '?navId=11542&tk=7&lk=9335',
        'ddr2': 'http://www.alternate.nl/html/product/listing.html'
                '?navId=11554&tk=7&lk=9312',
        'ddr3': 'http://www.alternate.nl/html/product/listing.html'
                '?navId=11556&bgid=8296&tk=7&lk=9326',
        'ddr4': 'http://www.alternate.nl/html/product/listing.html'
                '?navId=20678&tk=7&lk=13472'}

    mainboard_listings = {
        'amd': 'http://www.alternate.nl/html/product/listing.html?navId=11622&tk=7&lk=9419',
        'intel': 'http://www.alternate.nl/html/product/listing.html?navId=11626&tk=7&lk=9435'
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

    mobo_item_fields = {

    }

    start_urls = cpu_listings + list(gpu_listings.values()) + list(memory_listings.values()) + list(mainboard_listings.values())

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        rows = hxs.select('//div[@class="listRow"]')
        for row in rows:
            product = Product()
            product['manufacturer'] = row.select(self.item_field['manufacturer']).extract()
            product['name'] = row.select(self.item_field['name']).extract()
            product['price'] = row.select(self.item_field['price_big']).extract() + \
                               row.select(self.item_field['price_small']).extract()
            # if response.url in self.cpu_listings:
            #     yield self.get_cpu(row, product)
            # elif response.url in self.gpu_listings.values():
            #     yield self.get_gpu(row, product)
            # elif response.url in self.memory_listings.values():
            #     yield self.get_memory(row, product)
            if response.url in self.mainboard_listings.values():
                yield self.get_mainbord(row, product, response)

    def get_gpu(self, row, item):
        GPUItem.convert(item)
        item['chipset'] = row.select(self.item_field['info_one']).extract()
        item['mem_type'] = row.select(self.item_field['info_two']).extract()
        item['mem_amount'] = row.select(self.item_field['info_two']).extract()
        item['slots'] = row.select(self.item_field['info_three']).extract()
        return item

    def get_cpu(self, row, item):
        CPUItem.convert(item)
        item['speed'] = row.select(self.item_field['info_one']).extract()
        item['cores'] = row.select(self.item_field['info_two']).extract()
        item['socket'] = row.select(self.item_field['info_three']).extract()
        return item

    def get_memory(self, row, item):
        MemoryItem.convert(item)
        item['type'] = item['name']
        item['amount'] = row.select(self.item_field['info_one']).extract()
        item['slots'] = row.select(self.item_field['info_three']).extract()
        return item

    def get_mainbord2(self, response):
        item = response.meta['item']
        attributes = [unidecode(i) for i in response.xpath('//*[@id="details"]/div[4]/div/table/tr/td[@class="techDataCol2"]//td/text()').extract()]
        for attribute_key in attributes:
            usb_slots_pattern = re.match(r'(\d)x USB 2.0', attribute_key)
            attribute_index = attributes.index(attribute_key) + 1
            if attribute_index < len(attributes):
                attribute_value = attributes[attribute_index]
                if attribute_key == 'Geheugen socket':
                    item['mem_slots'] = attribute_value
                elif attribute_key == 'Maximaal':
                    item['mem_max'] = attribute_value
                elif attribute_key == 'SATA':
                    item['sata_slots'] = attribute_value
                elif usb_slots_pattern:
                    item['usb_slots'] = usb_slots_pattern.group(1)
        return item

    def get_mainbord(self, row, item, response):
        MainboardItem.convert(item)
        item['socket'] = row.select(self.item_field['info_three']).extract()
        item['formfactor'] = row.select(self.item_field['info_one']).extract()
        parsed_url = urlparse(response.url)
        link = parsed_url.scheme + '://' + parsed_url.netloc + row.select('a[@class="productLink"]/@href').extract()[0]
        request = scrapy.Request(link, callback=self.get_mainbord2)
        request.meta['item'] = item
        return request
