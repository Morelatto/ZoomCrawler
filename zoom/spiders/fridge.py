# -*- coding: utf-8 -*-
import scrapy

from zoom.items import FridgeLoader


class ZoomFridgeSpider(scrapy.Spider):
    name = 'zoom_fridges'

    start_urls = ['https://www.zoom.com.br/geladeira/preco-ate-2400/frost-free/capacidade-300-a-349-litros/capacidade-350-a-449-litros']

    def parse(self, response):
        for fridge_link in response.css('.tp-default .name-link::attr(href)').extract():
            yield scrapy.Request('https://www.zoom.com.br' + fridge_link, callback=self.parse_fridge)

        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page not in (None, 'javascript:void(0);'):
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @classmethod
    def parse_fridge(cls, response):
        # TODO replace css with xpath like oven
        fridge_loader = FridgeLoader(selector=response.css('.tech-spec-table tbody'))
        fridge_loader.add_xpath('name', '//h1[@class="product-name"]/span/text()')
        fridge_loader.add_xpath('rating', '//div[@class="rating"]/span/@class')
        fridge_loader.add_xpath('price', '//a[@class="price-label"]/strong/text()')

        basic_info_loader = fridge_loader.nested_css(':nth-child(1) tr')
        basic_info_loader.add_css('brand', ':nth-child(2) .table-val a::text')
        basic_info_loader.add_css('model', ':nth-child(3) .table-val::text')
        basic_info_loader.add_css('total_capacity', ':nth-child(5) .table-val a::text')
        basic_info_loader.add_css('cooler_capacity', ':nth-child(6) .table-val span::text')
        basic_info_loader.add_css('freezer_capacity', ':nth-child(7) .table-val span::text')

        details_loader = fridge_loader.nested_css(':nth-child(2) tr')
        details_loader.add_css('door', ':nth-child(2) .table-val a::text')
        details_loader.add_css('special_resources', ':nth-child(3) .table-val span::text')
        details_loader.add_css('basic_resources', ':nth-child(4) .table-val span::text')
        details_loader.add_css('external_dispenser', ':nth-child(5) .table-val span::text')
        details_loader.add_css('door_material', ':nth-child(6) .table-val span::text')
        details_loader.add_css('shelf_material', ':nth-child(7) .table-val span::text')

        freezer_info_loader = fridge_loader.nested_css(':nth-child(3) tr')
        freezer_info_loader.add_css('freezer_resources', ':nth-child(2) .table-val span::text')
        freezer_info_loader.add_css('defrost_type', ':nth-child(3) .table-val a::text')

        energetic_efficiency_loader = fridge_loader.nested_css(':nth-child(4) tr')
        energetic_efficiency_loader.add_css('energetic_efficiency', ':nth-child(2) .table-val a::text')

        specifications_loader = fridge_loader.nested_css(':nth-child(6) tr')
        specifications_loader.add_css('height', ':nth-child(2) .table-val a::text')
        specifications_loader.add_css('width', ':nth-child(3) .table-val a::text')
        specifications_loader.add_css('depth', ':nth-child(4) .table-val a::text')
        specifications_loader.add_css('weight', ':nth-child(5) .table-val span::text')
        specifications_loader.add_css('voltage', ':nth-child(6) .table-val span::text')
        specifications_loader.add_css('consumption', ':nth-child(7) .table-val span::text')

        yield fridge_loader.load_item()
