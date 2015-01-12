# -*- coding: utf-8 -*-
import json
from miner.items import CPUItem, GPUItem, MemoryItem, MainboardItem, CaseItem, PSUItem, HDDItem
import os
import requests
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
from miner.basepipeline import BasePipeline


class CsvWriterPipeline(object):
    def __init__(self):
        self.files = {
            "Grafische kaart": 'gpus.csv',
            "Moederbord": 'mobos.csv',
            "Processor": 'cpus.csv',
            "Voeding": 'psus.csv',
            "Behuizing": 'cases.csv',
            "Geheugen": 'memory.csv',
            'Harde schijf': 'hdds.csv'
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
        directory = 'data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        for k, v in list(self.files.items()):
            self.files[k] = open(os.path.join(directory, v), 'wb')
            self.exporters[k] = CsvItemExporter(self.files[k], delimiter=';')
            self.exporters[k].start_exporting()

    def spider_closed(self, spider):
        for i in list(self.files.keys()):
            self.exporters[i].finish_exporting()
            self.files[i].close()


class ValidationPipeline(BasePipeline):
    def process_item(self, item, spider):
        if spider.name == 'alternate':
            item = self.clean_fields(item)
        item['hash'] = self.generate_id(item, spider)
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
        elif isinstance(item, HDDItem):
            item['capacity'] = self.cleanup_field(item['capacity'])
        return item


class PostRequestPipeline(object):
    def __init__(self):
        self.paths = {
            "Grafische kaart": 'videokaarten',
            "Moederbord": 'moederborden',
            "Processor": 'processoren',
            "Voeding": 'voedingen',
            "Behuizing": 'behuizingen',
            "Geheugen": 'geheugen',
            'Harde schijf': 'harddisks'
        }
        try:
            server = os.environ('OPENSHIFT_APP_DNS')
        except KeyError:
            server = 'http://127.0.0.1:5000/'
        server = server + "api/"

    def process_item(self, item, spider):
        url = server + self.paths[item['product_type']]
        headers = {'Content-Type': 'application/json'}

        filters = [dict(name='hash', op='eq', val=item['hash'])]
        params = dict(q=json.dumps(dict(filters=filters)))

        exists = requests.get(url, params=params, headers=headers)
        if exists.status_code != 200:
            requests.post(url,
                          data=json.dumps(dict(item)),
                          headers=headers)
        return item