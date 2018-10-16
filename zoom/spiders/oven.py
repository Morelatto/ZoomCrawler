# -*- coding: utf-8 -*-
import scrapy

from zoom.items import OvenLoader


class ZoomStoveSpider(scrapy.Spider):
    name = 'zoom_ovens'

    start_urls = [
        'https://www.zoom.com.br/fogao/preco-ate-1000/fogao-de-piso?resultsperpage=72&unavailable=1&resultorder=2']

    def parse(self, response):
        for stove_link in response.css('.tp-default .name-link::attr(href)').extract():
            yield scrapy.Request('https://www.zoom.com.br' + stove_link, callback=self.parse_oven)

        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page not in (None, 'javascript:void(0);'):
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @classmethod
    def parse_oven(cls, response):
        oven_loader = OvenLoader(selector=response.css('.tech-spec-table tbody'))
        oven_loader.add_xpath('nome', '//h1[@class="product-name"]/span/text()')
        oven_loader.add_xpath('rating', '//div[@class="rating"]/span/@class')
        oven_loader.add_xpath('preco', '//a[@class="price-label"]/strong/text()')

        basic_info_loader = oven_loader.nested_css(':nth-child(1) tr')
        basic_info_loader.add_css('marca', ':nth-child(2) .table-val a::text')
        basic_info_loader.add_css('modelo', ':nth-child(3) .table-val::text')

        stove_info_loader = oven_loader.nested_css(':nth-child(2) tr')
        stove_info_loader.add_css('tipo', ':nth-child(2) .table-val a::text')
        stove_info_loader.add_css('bocas', ':nth-child(3) .table-val a::text')
        stove_info_loader.add_css('funcionamento_mesa', ':nth-child(4) .table-val a::text')
        stove_info_loader.add_css('acendimento_mesa', ':nth-child(5) .table-val a::text')
        stove_info_loader.add_css('acabamento_inox', ':nth-child(6) .table-val a::text')
        stove_info_loader.add_css('acabamento_inox', ':nth-child(6) .table-val span::text')
        stove_info_loader.add_css('material_mesa', ':nth-child(7) .table-val span::text')
        stove_info_loader.add_css('funcoes_mesa', ':nth-child(8) .table-val a::text')
        stove_info_loader.add_css('tipo_grade', ':nth-child(9) .table-val span::text')

        oven_info_loader = oven_loader.nested_css(':nth-child(3) tr')
        oven_info_loader.add_css('capacidade_forno', ':nth-child(2) .table-val span::text')
        oven_info_loader.add_css('prateleiras_forno', ':nth-child(3) .table-val span::text')
        oven_info_loader.add_css('funcoes_forno', ':nth-child(4) .table-val a::text')
        oven_info_loader.add_css('funcoes_especiais_forno', ':nth-child(5) .table-val a::text')

        energetic_efficiency_loader = oven_loader.nested_css(':nth-child(4) tr')
        energetic_efficiency_loader.add_css('energetic_efficiency', ':nth-child(2) .table-val a::text')

        specifications_loader = oven_loader.nested_css(':nth-child(6) tr')
        specifications_loader.add_css('altura', ':nth-child(2) .table-val a::text')
        specifications_loader.add_css('largura', ':nth-child(3) .table-val a::text')
        specifications_loader.add_css('profundidade', ':nth-child(4) .table-val a::text')
        specifications_loader.add_css('peso', ':nth-child(5) .table-val span::text')
        specifications_loader.add_css('voltagem', ':nth-child(6) .table-val span::text')

        yield oven_loader.load_item()
