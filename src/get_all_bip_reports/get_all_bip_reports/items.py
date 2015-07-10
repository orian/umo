# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
import scrapy


class GetAllBipReportsItem(Item):
  # define the fields for your item here like:
  # name = scrapy.Field()
  pass

class FiledownloadItem(Item):
  name = Field()
  file_urls = Field()
  files = Field()

  text = Field()
  url = Field()
  ref = Field()

class PageItem(Item):
  text = Field()
  url = Field()
  ref = Field()