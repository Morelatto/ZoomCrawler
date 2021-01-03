#!/usr/bin/env python3
"""Script to download product information from zoom.com.br

Usage:
  zoom.py <category_url>...
  zoom.py -h | --help | --version

Arguments:
  <category_url>...     List of category or subcategory urls to crawl. Ex.: tv/smart-tv tv

Options:
  -h, --help            Show this help message.
  --version             Show version.
"""
import sys

from docopt import docopt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zoom.spiders.zoom import ZoomSpider

ZOOM = 'https://www.zoom.com.br/'


def execute(cat_urls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(ZoomSpider, cat_urls=cat_urls)
    process.start()
    process.stop()


if __name__ == '__main__':
    args = docopt(__doc__, version='0.2')
    execute(args['<category_url>'])
    sys.exit(0)
