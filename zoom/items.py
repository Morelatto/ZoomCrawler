# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.loader.processors import Compose, TakeFirst, Join, MapCompose
from w3lib.html import strip_html5_whitespace


def get_last(l):
    return l.split()[-1] if l is not None and len(l) > 0 else None


def parse_row(r):
    rk = next(iter(r))
    rv = map(str.strip, r[rk])
    return {rk: next(rv) if len(r[rk]) == 1 else list(rv)}


def squash_dict(L):
    return {k: v for d in L for k, v in d.items()}


def get_numbers(s):
    return re.findall(r'\d', s)


def format_usefulness(u):
    if u[0] != '0': u[0] = '+' + u[0]
    if u[1] != '0': u[1] = '-' + u[1]
    return u


_name = scrapy.Field(input_processor=MapCompose(strip_html5_whitespace), output_processor=Compose(TakeFirst()))
_currency = scrapy.Field(output_processor=Compose(TakeFirst(), get_last))
_stars = scrapy.Field(output_processor=Compose(TakeFirst(), get_numbers, Join('.')))


class ProductItem(scrapy.Item):
    name = _name
    category = _name
    url = scrapy.Field(output_processor=Compose(TakeFirst()))
    price = _currency
    store = _name
    offer_list = scrapy.Field()


class ProductOffer(scrapy.Item):
    store = _name
    price_cash = scrapy.Field(output_processor=Compose(Join(''), get_last))
    price_parcel = _currency
    parcel_amount = scrapy.Field(output_processor=Compose(TakeFirst(), lambda v: v.split('x')[0]))

    def __repr__(self):
        return str(dict(self))


class UserRating(scrapy.Item):
    name = _name
    stars = _stars
    ratings = scrapy.Field(output_processor=Compose(TakeFirst(), get_numbers, TakeFirst()))
    approval_rate = _name
    comments = scrapy.Field()


class UserComment(scrapy.Item):
    username = _name
    use = _name
    date = scrapy.Field(input_processor=MapCompose(lambda d: d.split('em ')),
                        output_processor=Compose(TakeFirst()))
    title = scrapy.Field(output_processor=Compose(TakeFirst()))
    stars = _stars
    recommended = _name
    text = scrapy.Field(output_processor=Compose(TakeFirst()))
    useful = scrapy.Field(output_processor=format_usefulness)


class PriceHistory(scrapy.Item):
    name = _name
    history = scrapy.Field(output_processor=Compose(TakeFirst()))


class TechSpecTable(scrapy.Item):
    name = _name
    rows = scrapy.Field(input_processor=Compose(TakeFirst(), parse_row), output_processor=squash_dict)
