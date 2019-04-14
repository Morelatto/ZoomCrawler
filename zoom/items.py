# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.loader.processors import Compose, TakeFirst, Join


def get_last(l):
    return l.split()[-1] if l is not None and len(l) > 0 else None


remove_currency = Compose(TakeFirst(), get_last)


class TvItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    stars = scrapy.Field(output_processor=Compose(TakeFirst(), lambda v: re.findall(r'\d-\d', v)))
    ratings = scrapy.Field(output_processor=Compose(lambda v: v[-1] if len(v) > 1 else None,
                                                    lambda v: re.findall(r'\d+', v), TakeFirst()))
    lowest_price_last_40 = scrapy.Field(output_processor=remove_currency)
    lowest_price_today = scrapy.Field(output_processor=remove_currency)
    offer_list = scrapy.Field()
    tech_spec_table = scrapy.Field()


class TvOffer(scrapy.Item):
    store = scrapy.Field(output_processor=TakeFirst())
    price_cash = scrapy.Field(output_processor=Compose(Join(''), get_last))
    price_parcel = scrapy.Field(output_processor=remove_currency)
    parcel_amount = scrapy.Field(output_processor=Compose(TakeFirst(), lambda v: v.split('x')[0]))
    parcel_total = scrapy.Field(output_processor=remove_currency)  # TODO confirm db

    def __repr__(self):
        return str(dict(self))


class PriceHistory(scrapy.Item):
    default_output_processor = TakeFirst()
    name = scrapy.Field()
    history = scrapy.Field()


class TableItem(scrapy.Item):
    row = scrapy.Field()


'''
create table TV_ITEM (item_id integer, model_id integer, store_id integer, price_cash real, price_parcel real, parcel_amount integer, parcel_total real); -- TODO select * from tv_item where price_parcel * parcel_amount != parcel_total; 
create table TV_MODEL(model_id integer, name text, model text); -- max_price real, min_price real);
create table STORES (store_id integer, name text);


'''
