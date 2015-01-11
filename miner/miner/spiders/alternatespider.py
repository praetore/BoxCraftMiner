# -*- coding: utf-8 -*-
import re
from urlparse import urlparse
import scrapy
from miner.items import CPUItem, GPUItem, Product, MemoryItem, MainboardItem, CaseItem, PSUItem, HDDItem


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
        'amd': 'http://www.alternate.nl/html/product/listing.html'
               '?filter_5=&filter_4=&filter_3=&filter_2=&filter_1=&size=500&lk=7&tk=7&navId=11622',
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
                       'sup/text()',
        'attributes': '//*[@id="details"]/div[4]/div/table/tr/td[@class="techDataCol2"]//td/text()'
    }

    case_listings = ['http://www.alternate.nl/html/product/listing.html?filter_5=&filter_4=&filter_3=&filter_2=&'
                     'filter_1=&size=500&bgid=8148&lk=9309&tk=7&navId=2436',
                     'http://www.alternate.nl/html/product/listing.html?filter_5=&filter_4=&filter_3=&filter_2=&'
                     'filter_1=&size=500&page=2&bgid=8148&lk=9309&tk=7&navId=2436']

    psu_listings = ['http://www.alternate.nl/html/product/listing.html?filter_5=&filter_4=&filter_3=&filter_2=&'
                    'filter_1=&size=500&bgid=8215&lk=9533&tk=7&navId=11604']

    hdd_listings = {
        "SSD": 'http://www.alternate.nl/html/product/listing.html?navId=11890&bgid=8985&tk=7&lk=9585',
        "SATA": 'http://www.alternate.nl/html/product/listing.html?navId=11584&bgid=8459&tk=7&lk=9563',
        "Hybride": 'http://www.alternate.nl/html/product/listing.html?navId=17557&bgid=8459&tk=7&lk=9601'
    }

    start_urls = cpu_listings + \
                 list(gpu_listings.values()) + \
                 list(memory_listings.values()) + \
                 list(mainboard_listings.values()) + \
                 case_listings + \
                 psu_listings + \
                 hdd_listings.values()

    def parse(self, response):
        rows = response.xpath('//div[@class="listRow"]')
        for row in rows:
            item = Product()
            item['manufacturer'] = row.xpath(self.item_field['manufacturer']).extract()
            item['name'] = row.xpath(self.item_field['name']).extract()
            item['price'] = row.xpath(self.item_field['price_big']).extract() + \
                            row.xpath(self.item_field['price_small']).extract()
            parsed_url = urlparse(response.url)
            item['link'] = parsed_url.scheme + '://' + parsed_url.netloc + \
                           row.xpath('a[@class="productLink"]/@href').extract()[0]
            item['img_link'] = parsed_url.scheme + '://' + parsed_url.netloc
            item['supplier'] = self.name.title()
            if response.url in self.cpu_listings:
                item['product_type'] = 'Processor'
                yield self.get_cpu(row, item)
            elif response.url in self.gpu_listings.values():
                item['product_type'] = 'Grafische kaart'
                yield self.get_gpu(row, item)
            elif response.url in self.memory_listings.values():
                item['product_type'] = 'Geheugen'
                yield self.get_memory(row, item)
            elif response.url in self.mainboard_listings.values():
                item['product_type'] = 'Moederbord'
                yield self.get_mainbord(row, item, response)
            elif response.url in self.case_listings:
                item['product_type'] = 'Behuizing'
                yield self.get_case(row, item, response)
            elif response.url in self.psu_listings:
                item['product_type'] = 'Voeding'
                yield self.get_psu(row, item, response)
            elif response.url in self.hdd_listings.values():
                item['product_type'] = 'Harde schijf'
                yield self.get_hdd(row, item, response)

    def get_hdd(self, row, item, response):
        HDDItem.convert(item)
        for k, v in self.hdd_listings.items():
            if response.url == v:
                item['type'] = k
                break
        item['capacity'] = row.select(self.item_field['info_one']).extract()
        request = scrapy.Request(item['link'], callback=self.get_hdd2)
        request.meta['item'] = item
        return request

    def get_hdd2(self, response):
        item = response.meta['item']
        item['img_link'] += response.xpath('//*[@id="bigPic"]/img/@src').extract()[0]
        attributes = [i for i in response.xpath(self.item_field['attributes']).extract()]
        if 'inch' not in attributes[2]:
            item['physical_size'] = 'Onbekend'
        else:
            item['physical_size'] = attributes[2]

        if 'ATA' not in attributes[5]:
            item['interface'] = 'Onbekend'
        else:
            item['interface'] = attributes[5]
        return item

    def get_gpu(self, row, item):
        GPUItem.convert(item)
        item['chipset'] = row.select(self.item_field['info_one']).extract()
        item['mem_type'] = row.select(self.item_field['info_two']).extract()
        item['mem_amount'] = row.select(self.item_field['info_two']).extract()
        item['slots'] = row.select(self.item_field['info_three']).extract()
        request = scrapy.Request(item['link'], callback=self.get_img_link)
        request.meta['item'] = item
        return request

    def get_cpu(self, row, item):
        CPUItem.convert(item)
        item['speed'] = row.select(self.item_field['info_one']).extract()
        item['cores'] = row.select(self.item_field['info_two']).extract()
        item['socket'] = row.select(self.item_field['info_three']).extract()
        request = scrapy.Request(item['link'], callback=self.get_img_link)
        request.meta['item'] = item
        return request

    def get_memory(self, row, item):
        MemoryItem.convert(item)
        item['type'] = item['name']
        item['amount'] = row.select(self.item_field['info_one']).extract()
        item['slots'] = row.select(self.item_field['info_three']).extract()
        request = scrapy.Request(item['link'], callback=self.get_img_link)
        request.meta['item'] = item
        return request

    def get_mainbord(self, row, item, response):
        MainboardItem.convert(item)
        item['socket'] = row.select(self.item_field['info_three']).extract()
        item['formfactor'] = row.select(self.item_field['info_one']).extract()
        request = scrapy.Request(item['link'], callback=self.get_mainbord2)
        request.meta['item'] = item
        return request

    def get_mainbord2(self, response):
        item = response.meta['item']
        item['img_link'] += response.xpath('//*[@id="bigPic"]/img/@src').extract()[0]
        attributes = [i for i in response.xpath(self.item_field['attributes']).extract()]
        for attribute_key in attributes:
            usb_slots_pattern = re.match(r'(\d)x USB 2.0', attribute_key)
            attribute_index = attributes.index(attribute_key) + 1
            if attribute_index < len(attributes):
                attribute_value = attributes[attribute_index]
                if attribute_key == 'Geheugen socket':
                    item['mem_slots'] = attribute_value.split('x')[0]
                elif attribute_key == 'Maximaal':
                    item['mem_max'] = attribute_value
                elif attribute_key == 'SATA':
                    item['sata_slots'] = attribute_value
                elif usb_slots_pattern:
                    item['usb_slots'] = usb_slots_pattern.group(1)
        return item

    def get_case(self, row, item, response):
        item['name'] = item['name'][0].replace(", behuizing", "")
        CaseItem.convert(item)
        item['formfactor_psu'] = row.select(self.item_field['info_three']).extract()
        item['external_525'] = row.select(self.item_field['info_one']).extract()
        item['external_35'] = row.select(self.item_field['info_one']).extract()
        item['internal_25'] = row.select(self.item_field['info_one']).extract()
        item['internal_35'] = row.select(self.item_field['info_one']).extract()
        request = scrapy.Request(item['link'], callback=self.get_case2)
        request.meta['item'] = item
        return request

    def get_case2(self, response):
        item = response.meta['item']
        attributes = [i for i in response.xpath(self.item_field['attributes']).extract()]
        if 'TX' not in attributes[0]:
            item['color'] = attributes[0]
        item['formfactor_mobo'] = attributes[1]
        item['img_link'] += response.xpath('//*[@id="bigPic"]/img/@src').extract()[0]
        return item

    def get_psu(self, row, item, response):
        PSUItem.convert(item)
        item['power'] = row.xpath(self.item_field['info_one']).extract()
        request = scrapy.Request(item['link'], callback=self.get_psu2)
        request.meta['item'] = item
        return request

    def get_psu2(self, response):
        item = response.meta['item']
        attributes = [i for i in response.xpath(self.item_field['attributes']).extract()]
        item['formfactor'] = attributes[0]
        item['img_link'] += response.xpath('//*[@id="bigPic"]/img/@src').extract()[0]
        return item

    def get_img_link(self, response):
        item = response.meta['item']
        item['img_link'] += response.xpath('//*[@id="bigPic"]/img/@src').extract()[0]
        return item