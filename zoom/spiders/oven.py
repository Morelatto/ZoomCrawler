# -*- coding: utf-8 -*-
import scrapy

from zoom.items import OvenLoader


class ZoomStoveSpider(scrapy.Spider):
    name = 'zoom_ovens'

    start_urls = ['https://www.zoom.com.br/fogao/preco-ate-1000/fogao-de-piso']

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
        oven_loader.add_xpath('avaliacoes', '//a[@class="vote-txt"]/span/text()')
        oven_loader.add_xpath('preco', '//a[@class="price-label"]/strong/text()')

        basic_info_loader = oven_loader.nested_css(':nth-child(1) tr')
        basic_info_loader.add_xpath('marca', './/*[text()[contains(.,"Marca")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_xpath('modelo', './/*[text()[contains(.,"Modelo")]]/../td[@class="table-val"]//text()')

        stove_info_loader = oven_loader.nested_css(':nth-child(2) tr')
        stove_info_loader.add_xpath('tipo', './/*[text()[contains(.,"Tipo de Fogão")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('bocas', './/*[text()[contains(.,"Número de Bocas")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('funcionamento_mesa', './/*[text()[contains(.,"Funcionamento da Mesa")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('acendimento_mesa', './/*[text()[contains(.,"Tipo de Acendimento da Mesa")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('acabamento_inox', './/*[text()[contains(.,"Acabamento Inox")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('material_mesa', './/*[text()[contains(.,"Material da Mesa")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('funcoes_mesa', './/*[text()[contains(.,"Funções e Recursos da Mesa")]]/../../td[@class="table-val"]//text()')
        stove_info_loader.add_xpath('tipo_grade', './/*[text()[contains(.,"Tipo de Grade")]]/../../td[@class="table-val"]//text()')

        oven_info_loader = oven_loader.nested_css(':nth-child(3) tr')
        oven_info_loader.add_xpath('capacidade_forno', './/*[text()[contains(.,"Capacidade do Forno")]]/../../td[@class="table-val"]//text()')
        oven_info_loader.add_xpath('prateleiras_forno', './/*[text()[contains(.,"Prateleiras do Forno")]]/../../td[@class="table-val"]//text()')
        oven_info_loader.add_xpath('funcoes_forno', './/*[text()[contains(.,"Funções e Recursos Básicos do Forno")]]/../../td[@class="table-val"]//text()')
        oven_info_loader.add_xpath('funcoes_especiais_forno', './/*[text()[contains(.,"Funções e Recursos Especiais do Forno")]]/../../td[@class="table-val"]//text()')

        energetic_efficiency_loader = oven_loader.nested_css(':nth-child(4) tr')
        energetic_efficiency_loader.add_xpath('energetic_efficiency', './/*[text()[contains(.,"Eficiência Energética")]]/../../td[@class="table-val"]//text()')

        specifications_loader = oven_loader.nested_css(':nth-child(6) tr')
        specifications_loader.add_xpath('altura', './/*[text()[contains(.,"Altura")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('largura', './/*[text()[contains(.,"Largura")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('profundidade', './/*[text()[contains(.,"Profundidade")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('peso', './/*[text()[contains(.,"Peso")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('voltagem', './/*[text()[contains(.,"Voltagem")]]/../../td[@class="table-val"]//text()')

        yield oven_loader.load_item()
