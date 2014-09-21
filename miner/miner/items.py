# -*- coding: utf-8 -*-
from scrapy import Field, Item


class Product(Item):
    id = Field()
    manufacturer = Field()
    name = Field()
    price = Field()


class CPUItem(Product):
    socket = Field()
    speed = Field()
    cores = Field()


class MemoryItem(Product):
    type = Field()
    amount = Field()
    slots = Field()


class MainboardItem(Product):
    socket = Field()
    formfactor = Field()
    mem_slots = Field()
    mem_max = Field()
    sata_slots = Field()
    usb_slots = Field()


class GPUItem(Product):
    chipset = Field()
    mem_type = Field()
    mem_amount = Field()
    slots = Field()