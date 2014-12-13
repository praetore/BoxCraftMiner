# -*- coding: utf-8 -*-
from scrapy import Field, Item


class Converter(object):
    @classmethod
    def convert(cls, obj):
        obj.__class__ = cls


class Product(Item):
    _id = Field()
    product_type = Field()
    manufacturer = Field()
    name = Field()
    price = Field()
    link = Field()
    img_link = Field()


class CPUItem(Product, Converter):
    socket = Field()
    speed = Field()
    cores = Field()


class MemoryItem(Product, Converter):
    type = Field()
    amount = Field()
    slots = Field()


class MainboardItem(Product, Converter):
    socket = Field()
    formfactor = Field()
    mem_slots = Field()
    mem_max = Field()
    sata_slots = Field()
    usb_slots = Field()


class GPUItem(Product, Converter):
    chipset = Field()
    mem_type = Field()
    mem_amount = Field()
    slots = Field()


class PSUItem(Product, Converter):
    formfactor = Field()
    power = Field()


class CaseItem(Product, Converter):
    formfactor_mobo = Field()
    formfactor_psu = Field()
    internal_35 = Field()
    internal_25 = Field()
    external_35 = Field()
    external_525 = Field()
    color = Field()


class HDDItem(Product, Converter):
    type = Field()
    physical_size = Field()
    interface = Field()
    capacity = Field()