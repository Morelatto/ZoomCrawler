# -*- coding: utf-8 -*-
import json
import scrapy

from scrapy import Selector
from scrapy.loader import ItemLoader
from zoom_tvs.items import TvItem, TvOffer, PriceHistory, get_last, TableItem

# CSS Selectors
TEXT_SEL = '::text'
TOTAL_PRODUCTS = '.products-amount' + TEXT_SEL
LIST_ITEM = '#storeFrontList .tp-default'
ITEM_URL = 'a.name-link'
PROD_ID = '.save-product'
NAME_AND_MODEL = '.prod-name a' + TEXT_SEL
NAME_AND_MODEL_2 = '.product-info h1 span' + TEXT_SEL
STARS_AND_RATINGS = '.rating span'
LOWEST_40 = '.min-price-40 .value' + TEXT_SEL
LOWEST_1 = '.min-price-today .value' + TEXT_SEL
OFFER_TABLE = '.prices'
TRUSTED_STORES = '.price-tools .title span:nth-child(2)' + TEXT_SEL
PRODUCT_LIST_ITEM = '.product-list li'
STORE_NAME = '.store-info img::attr(alt)'
PRICE_CASH = '.main-price-format .lbt'
PARCEL_PRICE = '.secondary-price-format .lbt'
PARCEL_AMOUNT = '.parc-compl-first strong' + TEXT_SEL
PARCEL_TOTAL = '.parc-compl-last' + TEXT_SEL
TECH_SPEC_TABLE = '.details'
TABLE_ROW = '.ti'
TABLE_ATTR = '.table-attr' + TEXT_SEL
TABLE_ATTR_WITH_DIV = '.table-attr .item' + TEXT_SEL
TABLE_VAL = '.table-val *' + TEXT_SEL
TABLE_TITLE = '.section-title' + TEXT_SEL
NEXT_PAGES = '.pagination .lbt'


class TvSpider(scrapy.Spider):
    name = 'tvs'
    allowed_domains = ['zoom.com.br']
    start_urls = ['https://www.zoom.com.br/tv/todos?resultsperpage=72&unavailable=1&resultorder=4']

    def parse(self, response):
        self.logger.info(response.css(TOTAL_PRODUCTS).extract_first().strip())
        for item in response.css(LIST_ITEM):
            url = item.css(ITEM_URL).attrib['href']
            assert url is not None
            yield scrapy.Request(response.urljoin(url), self.parse_tv)

            prod_id = item.css(PROD_ID).attrib['data-product-id']
            name = item.css(NAME_AND_MODEL).get()
            assert prod_id is not None
            assert name is not None
            yield scrapy.FormRequest(url='https://www.zoom.com.br/product_desk',
                                     formdata={'__pAct_': '_get_ph', '_ph_t': 'd', 'prodid': prod_id},
                                     callback=self.parse_price_history,
                                     meta={'name': name})

        pages = response.css(NEXT_PAGES)
        for page in pages:
            yield scrapy.Request(response.urljoin(page.attrib['rel']))

    def parse_tv(self, response):
        il = ItemLoader(item=TvItem(), response=response)
        il.add_css('name', NAME_AND_MODEL_2)
        il.add_css('stars', STARS_AND_RATINGS)
        il.add_css('ratings', STARS_AND_RATINGS)
        il.add_css('lowest_price_last_40', LOWEST_40)  # FIXME
        il.add_css('lowest_price_today', LOWEST_1)
        il.add_value('offer_list', self.get_tv_offers(il.nested_css(OFFER_TABLE)))
        il.add_value('tech_spec_table', self.get_tech_spec_table(il.nested_css(TECH_SPEC_TABLE)))
        yield il.load_item()

    def get_tv_offers(self, loader):
        name = loader.get_collected_values('name')
        trust = loader.get_css(TRUSTED_STORES)
        self.logger.info('%s - %s' % (name, trust))

        for offer in loader.get_css(PRODUCT_LIST_ITEM):
            pl = ItemLoader(item=TvOffer(), selector=Selector(text=offer))
            pl.add_css('store', STORE_NAME)
            pl.add_css('price_cash', PRICE_CASH + TEXT_SEL)
            pl.add_css('price_cash', '%s span%s' % (PRICE_CASH, TEXT_SEL))
            pl.add_css('price_parcel', PARCEL_PRICE + TEXT_SEL)
            pl.add_css('parcel_amount', PARCEL_AMOUNT)
            pl.add_css('parcel_total', PARCEL_TOTAL)

            yield pl.load_item()

    def parse_price_history(self, response):
        json_response = json.loads(response.body_as_unicode())
        history = dict()
        for point in json_response['points']:
            ddmm = point['x']['label']
            day, month = ddmm.split('/')
            value = point['y']['label']
            history[month] = {**history.get(month, {}), **{day: get_last(value)}}

        hl = ItemLoader(item=PriceHistory())
        hl.add_value('name', response.meta['name'])
        hl.add_value('history', history)
        yield hl.load_item()

    def get_tech_spec_table(self, loader):
        item = TableItem()
        rows = dict()
        for row in loader.get_css(TABLE_ROW):
            sel = Selector(text=row)
            row_key = sel.css(TABLE_ATTR).get(sel.css(TABLE_ATTR_WITH_DIV).get())
            row_value = sel.css(TABLE_VAL).getall()
            rows[row_key] = row_value

        self.logger.info('%s (%d)' % (loader.get_css(TABLE_TITLE), len(rows.keys())))
        item['row'] = rows
        yield item


''''
div.product-info 
 h1.product-name span@text() = name with model 
 div.rating span
  [0] @className(); star_(\\d-\\d) = stars
  [1] @text() = # avaliações
 a.price-label = price
  strong@text()
  span.decimal@text() = price decimal
  span.parcel-value@text()
 div.min-price-40 span.value@text() = lowest price last 40 days
 div.min-price-today span.value@text() = lowest price today

trocar cep? (shipping preview)

for li in ul.product-list
 div.store-info img.alt = store name
 div.main-price-format
  a.lbt
   @text() = store price
   span@text() = store price decimal
 div.secondary-price-format
  span.parc-compl-first strong@text() = parcel amount (10x de, remove de)
   a.lbt
    @text() = parcel price with decimal
  span.parc-compl-last@text() = total with parcels
  
 
distinct list of stores

table .tech-spec-table
 tbody 
  tr.tt th@text() = title
  tr.ti td.table-attr (if hasA() a@text() else if hasDiv() div@text() else @text() = key
  tr.ti td.table-val (if hasA() a@text() else @text() = value

TV(Item)
 name
 model
 stars
 ratings_amount
 tv_price_range
 
 
TVPriceRange(Item)
 store
 price_a_vista
 parcel_amount = scrapy.Field(output_processor=lambda: value.split('x')[0])
 price_parcel
 parcel_total

 
 
 

tree representation of html pages - crawling tree algorithm

'''
