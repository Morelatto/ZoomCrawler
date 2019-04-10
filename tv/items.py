# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader.processors import Compose


class TvItem(scrapy.Item):
    name = scrapy.Field(output_processor=Compose(lambda v: v.split(v.split()[-1])[0]))
    model = scrapy.Field(output_processor=Compose(lambda v: v.split()[-1]))
    stars = scrapy.Field()
    ratings_amount = scrapy.Field()
    tv_price_range = scrapy.Field()
