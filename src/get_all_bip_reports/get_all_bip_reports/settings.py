# -*- coding: utf-8 -*-

# Scrapy settings for get_all_bip_reports project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
# #'scrapy.contrib.pipeline.files.FilesPipeline',

BOT_NAME = 'get_all_bip_reports'

SPIDER_MODULES = ['get_all_bip_reports.spiders']
NEWSPIDER_MODULE = 'get_all_bip_reports.spiders'

ITEM_PIPELINES = {
    'get_all_bip_reports.files.FilesPipeline2': 500,
}
FILES_STORE = '/data/downloads'
DOWNLOAD_DELAY = 1.

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'get_all_bip_reports (+http://www.yourdomain.com)'
