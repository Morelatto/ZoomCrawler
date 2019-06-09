"""Script to download product information from zoom.com.br

Usage:
  zoom.py <category>...
  zoom.py --list-categories | --list-subcategories
  zoom.py -h | --help | --version

Arguments:
  <category>...         Category or subcategory names to parse.

Options:
  --list-categories     List all product categories.
  --list-subcategories  List all product sub categories.
  -h, --help            Show this help message.
  --version             Show version.
"""
import sys

import requests

from docopt import docopt
from parsel import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from zoom.spiders.zoom import ZoomSpider

ZOOM = 'https://www.zoom.com.br/'

headers = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


def fetch_categories():
    cats, r = list(), requests.get(ZOOM, headers=headers)
    if r.status_code == 200:
        i, sel = 1, Selector(text=r.text)
        for level1 in sel.css('.level1 > .cat-name'):
            name, link = level1.css('::text').get(), level1.attrib['href']
            cats.append((name, link))
            print(i, name)
            i += 1
    return cats


def fetch_subcategories():
    subs, r = list(), requests.get(ZOOM, headers=headers)
    if r.status_code == 200:
        i, sel = 1, Selector(text=r.text)
        for level2 in sel.css('.level2 > .cat-name'):
            name, link = level2.css('::text').get(), level2.attrib['href']
            subs.append((name, link))
            print(i, name)
            i += 1
    return subs


def execute(cat_urls):
    process = CrawlerProcess(get_project_settings())
    process.crawl(ZoomSpider, cats=';'.join(cat_urls))
    process.start()
    process.stop()


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    urls = []
    if args['<category>']:
        all_cats = fetch_categories() + fetch_subcategories()
        clean_str = lambda s: s.lower().strip()
        for arg_cat in set(args['<category>']):
            for cat in all_cats:
                if clean_str(arg_cat) == clean_str(cat[0]):
                    urls.append(cat[1])

        if not urls or (len(urls) != len(args['<category>'])):
            print('Category not found', urls, args['<category>'])
            sys.exit(1)

    elif args['--list-categories']:
        all_cats = fetch_categories()
        n = input('#')
        if n:
            for x in set(n.split(',')):
                urls.append(all_cats[int(x) - 1][1])

    elif args['--list-subcategories']:
        all_subs = fetch_subcategories()
        n = input('#')
        if n:
            for x in set(n.split(',')):
                urls.append(all_subs[int(x) - 1][1])

    execute(urls)
