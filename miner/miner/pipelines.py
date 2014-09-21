# -*- coding: utf-8 -*-
import hashlib
import re
from miner.items import CPUItem, GPUItem, MemoryItem
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter


def generate_id(item, spider):
    itemstring = spider.name + item['name'] + item['manufacturer']
    return hashlib.sha1(itemstring).hexdigest()


def cleanup_field(itemfield):
    return itemfield[0].encode('ascii', errors='ignore').strip().replace('  ', ' ')


def validate_price(itemfield):
    itemfield = cleanup_field(itemfield)
    itemfield = itemfield.replace('-', '0')
    itemfield = itemfield.replace(' ', '')
    itemfield = itemfield.replace('.', '')
    itemfield = itemfield.replace(',', '.')
    return float(itemfield)


def validate_numerical(itemfield):
    itemfield = cleanup_field(itemfield)
    return re.sub("[^0-9]", "", itemfield)


def get_memory_type(itemfield):
    itemfield = cleanup_field(itemfield)
    return re.search(r'DDR\d*-\d*', itemfield).group()


class CsvExporterPipeline(object):
    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_opened(self, spider):
        csvfile = open('%s_products.csv' % spider.name, 'w+b')
        self.files[spider.name] = csvfile
        self.exporter = CsvItemExporter(csvfile, delimiter=';')
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        csvfile = self.files.pop(spider.name)
        csvfile.close()


class ValidationPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'alternate':
            item = self.process_alternate(item)
        elif spider.name == 'computerstore':
            item = self.process_computerstore(item)
        item['id'] = generate_id(item, spider)
        return item

    def process_alternate(self, item):
        item['manufacturer'] = cleanup_field(item['manufacturer'])
        item['name'] = cleanup_field(item['name'])
        item['price'] = validate_price(item['price'])
        if isinstance(item, CPUItem):
            item['cores'] = validate_numerical(item['cores'])
            item['socket'] = cleanup_field(item['socket'])
            item['speed'] = validate_numerical(item['speed'])
            return item
        elif isinstance(item, GPUItem):
            item['chipset'] = cleanup_field(item['chipset'])
            item['mem_type'] = cleanup_field(item['mem_type'])
            item['mem_amount'] = cleanup_field(item['mem_amount'])
            item['slots'] = validate_numerical(item['slots'])
            return item
        elif isinstance(item, MemoryItem):
            item['type'] = get_memory_type(item['type'])
            item['amount'] = cleanup_field(item['amount'])
            item['slots'] = validate_numerical(item['slots'])
            return item

    def process_computerstore(self, item):
        return item