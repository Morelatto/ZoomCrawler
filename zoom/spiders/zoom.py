# -*- coding: utf-8 -*-
import json
import scrapy

from scrapy.loader import ItemLoader
from zoom.items import ProductItem, ProductOffer, PriceHistory, TechSpecTable, UserComment

ZOOM_DOMAIN = 'zoom.com.br'
ZOOM_URL = 'https://' + ZOOM_DOMAIN

# CSS Selectors
TEXT_SEL = '::text'
ATTR_SEL = '::attr(%s)'

# listing page
PRODUCT_LIST = '.card--prod .cardBody'
ITEM_URL = '.name' + ATTR_SEL % 'href'
ITEM_NAME = '.name' + TEXT_SEL
ITEM_PRICE = '.price .customValue *' + TEXT_SEL
ITEM_STORE = '.storeCount' + TEXT_SEL

# product page
PRODUCT_NAME = 'string(//h1[starts-with(@class,"OverviewArea_TitleText")])'
OFFER_LIST = '//li[starts-with(@class,"SimilarsList_ListItem")]'
OFFER_STORE = './/img[starts-with(@class,"MerchantBrand_BrandImage")]/@alt'
OFFER_PRICE_C = 'string(.//a[starts-with(@class,"PriceBox_Value")])'
OFFER_PRICE_I = 'string(.//span[starts-with(@class,"PaymentDetails_FirstLabel")])'
PRICE_VAR_LAST_40 = '//div[starts-with(@class,"ProductPageBody_WithoutHorizontalPadding")]/section/div/div[2]/div[2]/span/text()'
PRICE_VAR_TODAY = '//div[starts-with(@class,"ProductPageBody")]/section/div/div[2]/div[3]/span/text()'

# user ratings
APPROVAL_NUMBER = '.product-rating-status .number' + TEXT_SEL
STARS = '.rating span' + ATTR_SEL % 'class'

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

# spec table
TABLE_ROWS = '//tr[starts-with(@class,"DetailsSection_Row")]'
TABLE_KEY = 'string(.//th[starts-with(@class,"DetailsSection_Key")])'
TABLE_VAL = './/td[starts-with(@class,"DetailsSection_Value")]//text()'


class ZoomSpider(scrapy.Spider):
    name = 'zoom'
    allowed_domains = [ZOOM_DOMAIN]

    def __init__(self, cat_urls, **kwargs):
        super().__init__(**kwargs)
        self.cats = cat_urls

    def start_requests(self):
        for cat in self.cats:
            url = '{}/{}?page=1'.format(ZOOM_URL, cat)
            yield scrapy.Request(url, meta={'page': 1, 'cat': cat})

    def parse(self, response, **kwargs):
        for prod in response.css(PRODUCT_LIST):
            il = ItemLoader(item=ProductItem(), selector=prod)
            il.add_css('name', ITEM_NAME)
            il.add_value('category', response.meta['cat'])
            il.add_css('store', ITEM_STORE)
            il.add_css('url', ITEM_URL)
            il.add_css('price', ITEM_PRICE)
            item = il.load_item()
            self.logger.info(item)
            yield scrapy.Request(ZOOM_URL + item['url'], callback=self.parse_product_page, meta={'item': item})

        page = response.meta['page'] + 1
        if page <= 7:
            next_url = "{}={}".format(response.url[:-2], page)
            yield scrapy.Request(next_url, meta={'page': page, 'cat': response.meta['cat']})

    def parse_product_page(self, response):
        for offer in response.xpath(OFFER_LIST):
            ol = ItemLoader(item=ProductOffer(), selector=offer)
            ol.add_xpath('name', PRODUCT_NAME)
            ol.add_xpath('store', OFFER_STORE)
            ol.add_xpath('price_cash', OFFER_PRICE_C)
            ol.add_xpath('price_cash_number', OFFER_PRICE_C)
            ol.add_xpath('price_install', OFFER_PRICE_I)

            item = ol.load_item()
            self.logger.warn(item)
            yield item

        # for rating in response.css():
        #     ul = ItemLoader(item=UserRating(), selector=rating)
        #     ul.add_value('name', name)
        #     ul.add_css('stars', STARS)
        #     ul.add_value('ratings', ratings)
        #     ul.add_css('approval_rate', APPROVAL_NUMBER)
        #     self.add_comments(ul)
        #     return ul.load_item()

        tl = ItemLoader(item=TechSpecTable(), response=response)
        tl.add_xpath('name', PRODUCT_NAME)
        for row in response.xpath(TABLE_ROWS):
            rk = row.xpath(TABLE_KEY).get()
            rv = row.xpath(TABLE_VAL).getall()
            tl.add_value('rows', {rk: rv})

        yield tl.load_item()

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
