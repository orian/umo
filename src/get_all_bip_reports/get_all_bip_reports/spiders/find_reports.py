# -*- coding: utf-8 -*-
import re
import logging
import scrapy
from get_all_bip_reports import items
from scrapy.linkextractors import LinkExtractor

DEBUG=True
DEBUG_CNT = 0

class FindReportsSpider(scrapy.Spider):
  name = "find_reports"
  allowed_domains = ["olsztyn.eu"]
  start_urls = (
#    'http://www.olsztyn.eu/',
    'http://www.bip.olsztyn.eu/bip/folder/3098/sesje_rady_miasta/',
  )

  def __init__(self, start=None, *args, **kwargs):
    super(FindReportsSpider, self).__init__(*args, **kwargs)
    if start:
      self.start_urls = [start]
    elif start_many:
      self.start_urls = start_many.split(",")

  def print_links(self, name, links):
    return
    for link in links:
      logging.debug('{} {}[{}]'.format(name, link.text.encode('utf8'), link.url))

  KADENCJA_RE = re.compile(r'http://www.bip.olsztyn.eu/bip/folder/\d+/kadencja_\d+_\d+/.*')
  SESJA_RE = re.compile(r'http://www.bip.olsztyn.eu/bip/dokument/\d+/.*_sesja_rady_miasta_.*/')
  UCHWALA_RE=re.compile(r'http://www.bip.olsztyn.eu/bip/dokument/\d+/.*')
  PLIK_RE = re.compile(r'http://www.bip.olsztyn.eu/bip/plik/\d+/.*')


  def parse_kadencja(self, response):
#    'LIX Sesja Rady Miasta 24 września 2014 r.'
#    'http://www.bip.olsztyn.eu/bip/dokument/305103/lix_sesja_rady_miasta_24_wrzesnia_2014_r_/'
    le = LinkExtractor(allow=FindReportsSpider.SESJA_RE)
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
    le = LinkExtractor(allow=FindReportsSpider.PLIK_RE)
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
         allow=FindReportsSpider.UCHWALA_RE,
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
    le = LinkExtractor(allow=FindReportsSpider.PLIK_RE)
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


  def parse_main(self, response):
    le = LinkExtractor(allow=KADENCJA_RE)
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

  def parse(self, response):
    f = None
    if response.url == 'http://www.bip.olsztyn.eu/bip/folder/3098/sesje_rady_miasta/':
      f = self.parse_main
    elif FindReportsSpider.KADENCJA_RE.match(response.url):
      f = self.parse_kadencja
    elif FindReportsSpider.SESJA_RE.match(response.url):
      f = self.parse_sesja
    elif FindReportsSpider.UCHWALA_RE.match(response.url):
      f = self.parse_uchwala
    else:
      logging.warning('don\'t recognize url: {}', response.url)
      return

    for y in f(response):
      yield y
