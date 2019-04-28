# -*- coding: utf-8 -*-
import json
import scrapy

from scrapy.loader import ItemLoader
from zoom.items import TvItem, TvOffer, PriceHistory, TechSpecTable, UserRating

# CSS Selectors
TEXT_SEL = '::text'
# product list
TOTAL_PRODUCTS = '.products-amount' + TEXT_SEL
STORE_FRONT_LIST = '#storeFrontList .tp-default'
ITEM_URL = 'a.name-link'
NAME_AND_MODEL = '.prod-name a' + TEXT_SEL
NEXT_PAGES = '.pagination .lbt'
# price history
PROD_ID = '.save-product'
# offers
OFFER_TABLE = '.prices'
TRUSTED_STORES = '.price-tools .title span:nth-child(2)' + TEXT_SEL
PRODUCT_LIST_ITEM = '.product-list li'
STORE_NAME = '.store-info img::attr(alt)'
PRICE_CASH = '.main-price-format .lbt'
PARCEL_PRICE = '.secondary-price-format .lbt'
PARCEL_AMOUNT = '.parc-compl-first strong' + TEXT_SEL
# user ratings
APPROVAL_NUMBER = '.product-rating-status .number' + TEXT_SEL
STARS = '.rating span::attr(class)'
RATINGS = '.rating span' + TEXT_SEL
# tech_spec_table
TABLE_ROW = '.details .ti'
TABLE_ATTR = '.table-attr *' + TEXT_SEL
TABLE_VAL = '.table-val *' + TEXT_SEL


class TvSpider(scrapy.Spider):
    name = 'tvs'
    allowed_domains = ['zoom.com.br']
    start_urls = ['https://www.zoom.com.br/tv/todos?resultsperpage=72&unavailable=1&resultorder=4']

    def parse(self, response):
        def _css(selector, attr=None):
            if attr is None:
                res = tv.css(selector).get()
            else:
                res = tv.css(selector).attrib[attr]
            assert res is not None
            return res

        self.logger.info(response.css(TOTAL_PRODUCTS).get().strip())
        for tv in response.css(STORE_FRONT_LIST):
            url = _css(ITEM_URL, 'href')
            name = _css(NAME_AND_MODEL)
            yield scrapy.Request(response.urljoin(url), self.parse_tv, meta={'name': name})

            prod_id = _css(PROD_ID, 'data-product-id')
            yield scrapy.FormRequest(url='https://www.zoom.com.br/product_desk',
                                     formdata={'__pAct_': '_get_ph', '_ph_t': 'd', 'prodid': prod_id},
                                     callback=self.parse_price_history,
                                     meta={'name': name})

        pages = response.css(NEXT_PAGES)
        for page in pages:
            yield scrapy.Request(response.urljoin(page.attrib['rel']))

    def parse_tv(self, response):
        il = ItemLoader(item=TvItem(), response=response)
        il.add_value('name', response.meta['name'])
        self.add_tv_offers(il.nested_css(OFFER_TABLE))

        yield il.load_item()
        yield self.get_user_ratings(response)
        yield self.get_tech_spec_table(response)

    def add_tv_offers(self, loader):
        name = loader.get_collected_values('name')
        trust = loader.selector.css(TRUSTED_STORES)
        self.logger.info('%s - %s' % (name[0], trust.get()))

        for offer in loader.selector.css(PRODUCT_LIST_ITEM):
            pl = ItemLoader(item=TvOffer(), selector=offer)
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
