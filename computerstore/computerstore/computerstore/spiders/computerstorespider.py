# -*- coding: utf-8 -*-
import scrapy


class ComputerstoreSpiderSpider(scrapy.Spider):
    name = "computerstore"
    allowed_domains = ["computerstore.nl"]
    start_urls = (
        'http://www.computerstore.nl/',
    )

    def parse(self, response):
        pass
