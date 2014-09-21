# -*- coding: utf-8 -*-

# Scrapy settings for miner project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'miner'

SPIDER_MODULES = ['miner.spiders']
NEWSPIDER_MODULE = 'miner.spiders'
ITEM_PIPELINES = {'miner.pipelines.MinerPipeline': 100}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'miner (+http://www.yourdomain.com)'