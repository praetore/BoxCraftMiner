# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from miner.items import CPUItem, GPUItem, MemoryItem


class MinerPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'alternate':
            item = self.process_alternate(item)
        elif spider.name == 'computerstore':
            item = self.process_computerstore(item)
        return item

    def process_alternate(self, item):
        if isinstance(item, CPUItem):
            return item
        elif isinstance(item, GPUItem):
            return item
        elif isinstance(item, MemoryItem):
            return item

    def process_computerstore(self, item):
        return item