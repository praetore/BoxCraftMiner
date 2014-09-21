# -*- coding: utf-8 -*-

from miner.items import CPUItem, GPUItem, MemoryItem
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter


class MinerPipeline(object):
    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def process_item(self, item, spider):
        if spider.name == 'alternate':
            item = self.process_alternate(item)
        elif spider.name == 'computerstore':
            item = self.process_computerstore(item)
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

    def cleanup_field(self, itemfield):
        return itemfield[0].encode('ascii', errors='ignore').strip()

    def validate_price(self, itemfield):
        itemfield = self.cleanup_field(itemfield)
        itemfield = itemfield.replace('-', '0')
        itemfield = itemfield.replace(' ', '')
        itemfield = itemfield.replace('.', '')
        itemfield = itemfield.replace(',', '.')
        return float(itemfield)

    def process_alternate(self, item):
        item['manufacturer'] = self.cleanup_field(item['manufacturer'])
        item['name'] = self.cleanup_field(item['name'])
        item['price'] = self.validate_price(item['price'])
        if isinstance(item, CPUItem):
            # TODO: Convert to integer
            item['cores'] = self.cleanup_field(item['cores'])
            item['socket'] = self.cleanup_field(item['socket'])
            # TODO: Convert to integer
            item['speed'] = self.cleanup_field(item['speed'])
            return item
        elif isinstance(item, GPUItem):
            item['chipset'] = self.cleanup_field(item['chipset'])
            # TODO: Split into separate fields
            item['mem_type'] = self.cleanup_field(item['mem_type'])
            item['mem_amount'] = self.cleanup_field(item['mem_amount'])
            # TODO: Convert to integer
            item['slots'] = self.cleanup_field(item['slots'])
            return item
        elif isinstance(item, MemoryItem):
            item['type'] = self.cleanup_field(item['type'])
            item['amount'] = self.cleanup_field(item['amount'])
            # TODO: Convert to integer
            item['slots'] = self.cleanup_field(item['slots'])
            return item

    def process_computerstore(self, item):
        return item