# -*- coding: utf-8 -*-
import re
import logging
import scrapy
from get_all_bip_reports import items
from scrapy.linkextractors import LinkExtractor

DEBUG=False
DEBUG_CNT = 0

class FindReportsSpider(scrapy.Spider):
  name = "find_reports"
  allowed_domains = ["olsztyn.eu"]
  start_urls = (
#    'http://www.olsztyn.eu/',
    'http://www.bip.olsztyn.eu/bip/folder/3098/sesje_rady_miasta/',
  )

  def print_links(self, name, links):
    for link in links:
      logging.debug('{} {}[{}]'.format(name, link.text.encode('utf8'), link.url))

  def parse_kadencja(self, response):
#    'LIX Sesja Rady Miasta 24 września 2014 r.'
#    'http://www.bip.olsztyn.eu/bip/dokument/305103/lix_sesja_rady_miasta_24_wrzesnia_2014_r_/'
    r = re.compile(r'http://www.bip.olsztyn.eu/bip/dokument/\d+/.*_sesja_rady_miasta_.*/')
    le = LinkExtractor(allow=r)
    links = le.extract_links(response)
    self.print_links('sesje', links)
    cnt = 0
    for link in links:
      yield scrapy.Request(link.url, callback=self.parse_sesja)
      k = items.PageItem()
      k['text'] = link.text.encode('utf8')
      k['url'] = link.url
      k['ref'] = response.url
      yield k
      if cnt >= DEBUG_CNT and DEBUG:
        break
      cnt += 1

  def parse_uchwala(self, response):
    # generate list of files to download
    le = LinkExtractor(
         allow=re.compile(r'http://www.bip.olsztyn.eu/bip/plik/\d+/.*'))
    links = le.extract_links(response)
    self.print_links('files', links)
    cnt = 0
    for link in links:
      fi = items.FiledownloadItem()
      fi['file_urls'] = [link.url]
      fi['text'] = link.text.encode('utf8')
      fi['url'] = link.url
      fi['ref'] = response.url
      yield fi
      if cnt >= DEBUG_CNT and DEBUG:
        break
      cnt += 1

  def parse_sesja(self, response):
    # uchwaly
    uchwaly_le = LinkExtractor(
         allow=re.compile(r'http://www.bip.olsztyn.eu/bip/dokument/\d+/.*'),
         restrict_xpaths='//table')
    links = uchwaly_le.extract_links(response)
    self.print_links('uchwaly', links)
    cnt = 0
    for link in links:
      yield scrapy.Request(link.url, callback=self.parse_uchwala)
      k = items.PageItem()
      k['text'] = link.text.encode('utf8')
      k['url'] = link.url
      k['ref'] = response.url
      yield k
      if cnt >= DEBUG_CNT and DEBUG:
        break
      cnt += 1

    # files (glosowania, obecnosc)
    le = LinkExtractor(allow=re.compile(r'.*/bip/plik/\d+/.*'))
    links = le.extract_links(response)
    self.print_links('glosowania', links)
    cnt = 0
    for link in links:
      fi = items.FiledownloadItem()
      fi['file_urls'] = [link.url]
      fi['text'] = link.text.encode('utf8')
      fi['url'] = link.url
      fi['ref'] = response.url
      yield fi
      if cnt >= DEBUG_CNT and DEBUG:
        break
      cnt += 1


  def parse(self, response):
    r = re.compile(r'http://www.bip.olsztyn.eu/bip/folder/\d+/kadencja_\d+_\d+/.*')
    le = LinkExtractor(allow=r)
    links = le.extract_links(response)
    self.print_links('kadencje', links)
    cnt = 0

    k = items.PageItem()
    k['text'] = 'Sesje Rady Miasta'
    k['url'] = response.url
    k['ref'] = '<entry point>'
    yield k

    for link in links:
      yield scrapy.Request(link.url, callback=self.parse_kadencja)
      k = items.PageItem()
      k['text'] = link.text.encode('utf8')
      k['url'] = link.url
      k['ref'] = response.url
      yield k
      if cnt >= DEBUG_CNT and DEBUG:
        break
      cnt += 1
