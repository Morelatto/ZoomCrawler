# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader.processors import Compose, TakeFirst, Join


class TvItem(scrapy.Item):
    name = scrapy.Field(output_processor=Compose(lambda v: v.split(v.split()[-1])[0]))
    model = scrapy.Field(output_processor=Compose(lambda v: v.split()[-1]))
    stars = scrapy.Field(output_processor=TakeFirst())  # TODO debug type, lambda regex star_(\d-\d)
    ratings = scrapy.Field()  # TODO compose with lambda regex \d
    tv_price_range = scrapy.Field()


class TvPriceRange(scrapy.Item):
    store = scrapy.Field()
    price_cash = scrapy.Field(output_processor=Join())
    price_parcel = scrapy.Field()
    parcel_amount = scrapy.Field(output_processor=lambda v: v.split('x')[0])
    parcel_total = scrapy.Field()  # TODO confirm db, remove 'total a prazo'


'''
create table TV_ITEM (item_id integer, model_id integer, store_id integer, price_cash real, price_parcel real, parcel_amount integer, parcel_total real); -- TODO select * from tv_item where price_parcel * parcel_amount != parcel_total; 
create table TV_MODEL(model_id integer, name text, model text); -- max_price real, min_price real);
create table STORES (store_id integer, name text);


'''