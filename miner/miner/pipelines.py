# -*- coding: utf-8 -*-
import json
from miner.items import CPUItem, GPUItem, MemoryItem, MainboardItem, CaseItem, PSUItem
import os
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter, JsonItemExporter
from miner.basepipeline import BasePipeline


class CsvWriterPipeline(object):
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


class ValidationPipeline(BasePipeline):
    def process_item(self, item, spider):
        if spider.name == 'alternate':
            item = self.clean_fields(item)
        elif spider.name == 'computerstore':
            item = self.clean_fields(item)
        item['_id'] = self.generate_id(item, spider)
        return item

    def clean_fields(self, item):
        item['manufacturer'] = self.cleanup_field(item['manufacturer'])
        item['name'] = self.cleanup_field(item['name'])
        item['price'] = self.validate_price(item['price'])
        if isinstance(item, CPUItem):
            item['cores'] = self.validate_numerical(item['cores'])
            item['socket'] = self.cleanup_field(item['socket'])
            item['speed'] = self.validate_numerical(item['speed'])
        elif isinstance(item, GPUItem):
            item['chipset'] = self.cleanup_field(item['chipset'])
            item['mem_type'] = self.get_gpu_memory_amount_type(item['mem_type'], 2)
            item['mem_amount'] = self.get_gpu_memory_amount_type(item['mem_amount'], 1)
            item['slots'] = self.validate_numerical(item['slots'])
        elif isinstance(item, MemoryItem):
            item['type'] = self.get_memory_type(item['type'])
            item['amount'] = self.cleanup_field(item['amount'])
            item['slots'] = self.validate_numerical(item['slots'])
        elif isinstance(item, MainboardItem):
            item['socket'] = self.cleanup_field(item['socket'])
            item['formfactor'] = self.validate_formfactor(item['formfactor'])
            item['mem_slots'] = self.validate_numerical(item['mem_slots'])
            item['mem_max'] = self.cleanup_field(item['mem_max'])
            item['sata_slots'] = self.validate_numerical(item['sata_slots'])
            item['usb_slots'] = self.validate_numerical(item['usb_slots'])
        elif isinstance(item, CaseItem):
            item['formfactor_mobo'] = self.validate_formfactor(item['formfactor_mobo'])
            item['formfactor_psu'] = self.validate_mobo_psu(item['formfactor_psu'])
            item['color'] = self.validate_colors(item['color'], self._validcolors)
            item['internal_35'] = self.get_bay_type_amount(item['internal_35'], '3,5 intern')
            item['internal_25'] = self.get_bay_type_amount(item['internal_25'], '2,5')
            item['external_35'] = self.get_bay_type_amount(item['external_35'], '3,5 extern')
            item['external_525'] = self.get_bay_type_amount(item['external_525'], '5,25')
        elif isinstance(item, PSUItem):
            item['power'] = self.validate_numerical(item['power'])
        return item


class JsonWriterPipeline(object):
    def __init__(self):
        self.files = {
            "Grafische kaart": 'gpus.json',
            "Moederbord": 'mobos.json',
            "Processor": 'cpus.json',
            "Voeding": 'psus.json',
            "Behuizing": 'cases.json',
            "Geheugen": 'memory.json'
        }
        self.exporters = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def process_item(self, item, spider):
        self.exporters[item["product_type"]].export_item(item)
        return item

    def spider_opened(self, spider):
        for k, v in list(self.files.items()):
            self.files[k] = open(os.path.join('data', v), 'wb')
            self.exporters[k] = JsonItemExporter(self.files[k])
            self.exporters[k].start_exporting()

    def spider_closed(self, spider):
        for i in list(self.files.keys()):
            self.exporters[i].finish_exporting()
            self.files[i].close()