# -*- coding: utf-8 -*-
import scrapy


class TvSSpider(scrapy.Spider):
    name = 'tv_s'
    allowed_domains = ['zoom.com.br']
    start_urls = ['https://www.zoom.com.br/tv/preco-1500-ou-mais/smart-tv/48-polegadas/49-/tamanho-50-polegadas/'
                  'tamanho-51-polegadas/tamanho-55-polegadas/tamanho-58-polegadas/tamanho-60-polegadas-ou-mais/'
                  'tamanho-65-polegadas/tamanho-70-polegadas-ou-mais/ultra-definicao-4k-/full-hd/8k']

    def parse(self, response):
        pass

    def parse_tv(self, response):
        tv = TvItem
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
 div.image-store-attr div.store-info img.alt = store name
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
 
il = ItemLoader(item=TV())
il.add ...
il.load_item()
 
 
 

tree representation of html pages - crawling tree algorithm

'''