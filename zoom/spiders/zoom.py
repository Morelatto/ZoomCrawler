# -*- coding: utf-8 -*-
import json
import scrapy

from scrapy.loader import ItemLoader
from zoom.items import ProductItem, ProductOffer, PriceHistory, TechSpecTable, UserRating, UserComment

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
# comments
COMM_USER_LIST = '.review-list .user'
COMM_REVIEW_LIST = '.review-list .review'
COMM_USER_NAME = '.user-name' + TEXT_SEL
COMM_USE_FREQUENCY = 'span' + TEXT_SEL
COMM_DATE = '.date' + TEXT_SEL
COMM_TITLE = '.title' + TEXT_SEL
COMM_STARS = '.product-rating span' + ATTR_SEL % 'class'
COMM_RECOMMENDS = '.recommendation' + TEXT_SEL
COMM_TEXT = '.text' + TEXT_SEL
COMM_USEFULNESS = '.counter' + TEXT_SEL
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
            yield scrapy.Request('https://www.{}{}/todos?{}'.format(ZOOM, cat, SEARCH_PARAMS), meta={'cat': cat})

    def parse(self, response):
        category = response.meta['cat']
        total_offers = response.css(TOTAL_OFFERS).get()
        if total_offers:
            self.logger.info(total_offers.strip())
            for offer in response.css(OFFER_LIST):
                url = offer.css(OFFER_URL).attrib['href']
                name = offer.css(OFFER_NAME).get()
                yield scrapy.Request(response.urljoin(url), self.parse_offers, meta={'name': name, 'cat': category})

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
                il.add_value('category', category)
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
        il.add_value('category', response.meta['cat'])
        self.add_offers(il.nested_css(OFFER_TABLE))

        yield il.load_item()
        yield self.get_user_ratings(response)
        yield self.get_tech_spec_table(response)

    def add_offers(self, loader):
        name = loader.get_collected_values('name')
        trust = loader.selector.css(TRUSTED_STORES)
        self.logger.info('%s - OFFERS(%s)' % (name[0], trust.get()))

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
        ratings = response.css(RATINGS).get()
        if ratings != '0 avaliações':
            self.logger.debug('%s - RATING(%s)' % (name, ratings))

            ul = ItemLoader(item=UserRating(), response=response)
            ul.add_value('name', name)
            ul.add_css('stars', STARS)
            ul.add_value('ratings', ratings)
            ul.add_css('approval_rate', APPROVAL_NUMBER)
            self.add_comments(ul)
            return ul.load_item()

    def get_tech_spec_table(self, response):
        name = response.meta['name']
        rows = response.css(TABLE_ROW)
        self.logger.debug('%s TECH(%s)' % (name, len(rows)))

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
        if hl.get_collected_values('history'):
            yield hl.load_item()

    def add_history(self, loader, response):
        json_response = json.loads(response.body_as_unicode())
        points = json_response['points']
        if points:
            self.logger.debug('%s - HIST(%s)' % (response.meta['name'], json_response.get('title')))
            history = dict()
            for point in points:
                ddmm = point['x']['label']
                day, month = ddmm.split('/')
                value = point['y']['value']
                history[month] = {**history.get(month, {}), **{day: float("{0:.2f}".format(value))}}
            loader.add_value('history', history)

    def add_comments(self, loader):
        users = loader.selector.css(COMM_USER_LIST)
        reviews = loader.selector.css(COMM_REVIEW_LIST)
        self.logger.debug('%s COMMS(%s, %s)' % (loader.get_output_value('name'), len(users), len(reviews)))
        for user, review in zip(users, reviews):
            cl = ItemLoader(item=UserComment(), selector=review)
            cl.add_value('username', user.css(COMM_USER_NAME).getall())
            cl.add_value('use', user.css(COMM_USE_FREQUENCY).get())
            cl.add_css('date', COMM_DATE)
            cl.add_css('title', COMM_TITLE)
            cl.add_css('stars', COMM_STARS)
            cl.add_css('recommended', COMM_RECOMMENDS)
            cl.add_css('text', COMM_TEXT)
            cl.add_css('useful', COMM_USEFULNESS)
            loader.add_value('comments', cl.load_item())
