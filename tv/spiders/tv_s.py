# -*- coding: utf-8 -*-
import scrapy

from scrapy import Selector
from scrapy.loader import ItemLoader
from tv.items import TvItem, TvOffer

# CSS Selectors
TEXT_SEL = '::text'
TOTAL_PRODUCTS = '.products-amount' + TEXT_SEL
NAME_AND_MODEL = '.product-info h1 span' + TEXT_SEL
STARS_AND_RATINGS = '.rating span'
OFFER_TABLE = '.prices'
TRUSTED_STORES = '.price-tools .title span:nth-child(2)' + TEXT_SEL
STORE_NAME = '.store-info img::attr(alt)'
PRICE_CASH = '.main-price-format .lbt'
PARCEL_PRICE = '.secondary-price-format .lbt'
PARCEL_AMOUNT = '.parc-compl-first strong' + TEXT_SEL
PARCEL_TOTAL = '.parc-compl-last' + TEXT_SEL


class TvSpider(scrapy.Spider):
    name = 'tvs'
    allowed_domains = ['zoom.com.br']
    start_urls = ['https://www.zoom.com.br/tv/preco-1500-ou-mais/smart-tv/48-polegadas/49-/tamanho-50-polegadas/'
                  'tamanho-51-polegadas/tamanho-55-polegadas/tamanho-58-polegadas/tamanho-60-polegadas-ou-mais/'
                  'tamanho-65-polegadas/tamanho-70-polegadas-ou-mais/ultra-definicao-4k-/full-hd/8k?resultsperpage=72']

    def parse(self, response):
        self.logger.info(response.css(TOTAL_PRODUCTS).extract_first().strip())
        for href in response.xpath('//h2/a/@href').getall():
            yield scrapy.Request(response.urljoin(href), self.parse_tv)

    def parse_tv(self, response):
        il = ItemLoader(item=TvItem(), response=response)
        il.add_css('name', NAME_AND_MODEL)
        il.add_css('model', NAME_AND_MODEL)
        il.add_css('stars', STARS_AND_RATINGS)
        il.add_css('ratings', STARS_AND_RATINGS)
        il.add_value('offer_list', self.get_tv_offers(il.nested_css(OFFER_TABLE)))

        yield il.load_item()

    def get_tv_offers(self, loader):
        full_name = loader.get_collected_values('name')
        trust = loader.get_css(TRUSTED_STORES)
        self.logger.info('%s - %s' % (full_name, trust))

        for offer in loader.get_css('.product-list li'):
            pl = ItemLoader(item=TvOffer(), selector=Selector(text=offer))
            pl.add_css('store', STORE_NAME)
            pl.add_css('price_cash', PRICE_CASH + TEXT_SEL)
            pl.add_css('price_cash', '%s span%s' % (PRICE_CASH, TEXT_SEL))
            pl.add_css('price_parcel', PARCEL_PRICE + TEXT_SEL)
            pl.add_css('parcel_amount', PARCEL_AMOUNT)
            pl.add_css('parcel_total', PARCEL_TOTAL)
            yield pl.load_item()


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