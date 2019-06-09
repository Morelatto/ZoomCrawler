# -*- coding: utf-8 -*-
import json
import scrapy

from scrapy.loader import ItemLoader
from zoom.items import ProductItem, ProductOffer, PriceHistory, TechSpecTable, UserRating

ZOOM = 'zoom.com.br'

# CSS Selectors
TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'
NEXT_PAGES = '.pagination .lbt'
# offer list
TOTAL_OFFERS = '.products-amount' + TEXT_SEL
OFFER_LIST = '#storeFrontList .tp-default'
OFFER_URL = 'a.name-link'
OFFER_NAME = '.prod-name a' + TEXT_SEL
# products with no offers
TOTAL_PRODUCTS = '.offers-amount strong' + TEXT_SEL
PRODUCT_LIST = '.item[data-oid]'
ITEM_URL = '.o-lead' + ATTR_SEL % 'rel'
ITEM_NAME = '.o-name' + TEXT_SEL
ITEM_PRICE = '.o-price .value' + TEXT_SEL
ITEM_STORE = '.o-store' + TEXT_SEL
# price history
PROD_ID = '.save-product'
# offers
OFFER_TABLE = '.prices'
TRUSTED_STORES = '.price-tools .title span:nth-child(2)' + TEXT_SEL
PRODUCT_LIST_ITEM = '.product-list li'
STORE_NAME = '.store-info img' + ATTR_SEL % 'alt'
PRICE_CASH = '.main-price-format .lbt'
PARCEL_PRICE = '.secondary-price-format .lbt'
PARCEL_AMOUNT = '.parc-compl-first strong' + TEXT_SEL
# user ratings
APPROVAL_NUMBER = '.product-rating-status .number' + TEXT_SEL
STARS = '.rating span' + ATTR_SEL % 'class'
RATINGS = '.rating span' + TEXT_SEL
# tech_spec_table
TABLE_ROW = '.details .ti'
TABLE_ATTR = '.table-attr *' + TEXT_SEL
TABLE_VAL = '.table-val *' + TEXT_SEL

SEARCH_PARAMS = 'resultsperpage=72&unavailable=1&resultorder=4'  # ordenar por mais buscados


class ZoomSpider(scrapy.Spider):
    name = 'zoom'
    allowed_domains = [ZOOM]

    def __init__(self, cats='', **kwargs):
        super().__init__(**kwargs)
        self.cats = cats.split(';')

    def start_requests(self):
        for cat in self.cats:
            yield scrapy.Request('https://www.{}/{}/todos?{}'.format(ZOOM, cat, SEARCH_PARAMS))

    def parse(self, response):
        total_offers = response.css(TOTAL_OFFERS).get()

        if total_offers:
            self.logger.info(total_offers.strip())
            for offer in response.css(OFFER_LIST):
                url = offer.css(OFFER_URL).attrib['href']
                name = offer.css(OFFER_NAME).get()
                yield scrapy.Request(response.urljoin(url), self.parse_offers, meta={'name': name})

                prod_id = offer.css(PROD_ID).attrib['data-product-id']
                yield scrapy.FormRequest(url='https://www.{}/product_desk'.format(ZOOM),
                                         formdata={'__pAct_': '_get_ph', '_ph_t': 'd', 'prodid': prod_id},
                                         callback=self.parse_price_history,
                                         meta={'name': name})

        else:
            total_products = response.css(TOTAL_PRODUCTS).get()
            self.logger.info(total_products)
            for prod in response.css(PRODUCT_LIST):
                il = ItemLoader(item=ProductItem(), selector=prod)
                il.add_css('url', ITEM_URL)
                il.add_css('name', ITEM_NAME)
                il.add_css('price', ITEM_PRICE)
                il.add_css('store', ITEM_STORE)
                yield il.load_item()

        pages = response.css(NEXT_PAGES)
        for page in pages:
            yield scrapy.Request(response.urljoin(page.attrib['rel']))

    def parse_offers(self, response):
        il = ItemLoader(item=ProductItem(), response=response)
        il.add_value('name', response.meta['name'])
        self.add_offers(il.nested_css(OFFER_TABLE))

        yield il.load_item()
        yield self.get_user_ratings(response)
        yield self.get_tech_spec_table(response)

    def add_offers(self, loader):
        name = loader.get_collected_values('name')
        trust = loader.selector.css(TRUSTED_STORES)
        self.logger.info('%s - %s' % (name[0], trust.get()))

        for offer in loader.selector.css(PRODUCT_LIST_ITEM):
            pl = ItemLoader(item=ProductOffer(), selector=offer)
            pl.add_css('store', STORE_NAME)
            pl.add_css('price_cash', PRICE_CASH + TEXT_SEL)
            pl.add_css('price_cash', '%s span%s' % (PRICE_CASH, TEXT_SEL))
            pl.add_css('price_parcel', PARCEL_PRICE + TEXT_SEL)
            pl.add_css('parcel_amount', PARCEL_AMOUNT)
            loader.add_value('offer_list', pl.load_item())

    def get_user_ratings(self, response):
        name = response.meta['name']
        approval = response.css(APPROVAL_NUMBER).get().strip()
        self.logger.debug('%s - %s' % (name, approval))

        ul = ItemLoader(item=UserRating(), response=response)
        ul.add_value('name', name)
        ul.add_css('stars', STARS)
        ul.add_css('ratings', RATINGS)
        ul.add_value('approval_rate', approval)
        return ul.load_item()

    def get_tech_spec_table(self, response):
        name = response.meta['name']
        rows = response.css(TABLE_ROW)
        self.logger.debug('%s (%s)' % (name, len(rows)))

        tl = ItemLoader(item=TechSpecTable(), response=response)
        tl.add_value('name', response.meta['name'])
        for row in rows:
            rk = row.css(TABLE_ATTR).get()
            rv = row.css(TABLE_VAL).getall()
            tl.add_value('rows', {rk: rv})

        return tl.load_item()

    def parse_price_history(self, response):
        hl = ItemLoader(item=PriceHistory())
        hl.add_value('name', response.meta['name'])
        self.add_history(hl, response)
        yield hl.load_item()

    def add_history(self, loader, response):
        json_response = json.loads(response.body_as_unicode())
        self.logger.debug('%s - %s' % (response.meta['name'], json_response.get('title')))

        history = dict()
        for point in json_response['points']:
            ddmm = point['x']['label']
            day, month = ddmm.split('/')
            value = point['y']['value']
            history[month] = {**history.get(month, {}), **{day: float("{0:.2f}".format(value))}}
        loader.add_value('history', history)
