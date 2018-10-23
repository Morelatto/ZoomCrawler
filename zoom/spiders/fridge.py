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
        fridge_loader = FridgeLoader(selector=response.css('.tech-spec-table tbody'))
        fridge_loader.add_xpath('nome', '//h1[@class="product-name"]/span/text()')
        fridge_loader.add_xpath('rating', '//div[@class="rating"]/span/@class')
        fridge_loader.add_xpath('preco', '//a[@class="price-label"]/strong/text()')

        basic_info_loader = fridge_loader.nested_css(':nth-child(1) tr')
        basic_info_loader.add_css('marca', './/*[text()[contains(.,"Marca")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_css('modelo', './/*[text()[contains(.,"Modelo")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_css('capacidade_total', './/*[text()[contains(.,"Capacidade Total")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_css('capacidade_refrigerador', './/*[text()[contains(.,"Capacidade do Refrigerador")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_css('capacidade_freezer', './/*[text()[contains(.,"Capacidade do Congelador/Freezer")]]/../td[@class="table-val"]//text()')

        details_loader = fridge_loader.nested_css(':nth-child(2) tr')
        details_loader.add_css('tipo_porta', './/*[text()[contains(.,"Tipo de Porta")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('recursos_especiais_refrigerador', './/*[text()[contains(.,"Recursos Especiais do Refrigerador")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('recursos_basicos_refrigerador', './/*[text()[contains(.,"Recursos Básicos do Refrigerador")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('dispenser_externo', './/*[text()[contains(.,"Dispenser Externo")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('tipo_controle', './/*[text()[contains(.,"Tipo de Controle")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('acabamento_porta', './/*[text()[contains(.,"Acabamento Externo da Porta")]]/../td[@class="table-val"]//text()')
        details_loader.add_css('material_prateleira', './/*[text()[contains(.,"Material da Prateleira")]]/../td[@class="table-val"]//text()')

        freezer_info_loader = fridge_loader.nested_css(':nth-child(3) tr')
        freezer_info_loader.add_css('recursos_freezer', './/*[text()[contains(.,"Recursos do Congelador/Freezer")]]/../td[@class="table-val"]//text()')
        freezer_info_loader.add_css('tipo_degelo', './/*[text()[contains(.,"Tipo de Degelo")]]/../td[@class="table-val"]//text()')

        energetic_efficiency_loader = fridge_loader.nested_css(':nth-child(4) tr')
        energetic_efficiency_loader.add_css('eficiencia_energetica', './/*[text()[contains(.,"Eficiência Energética")]]/../td[@class="table-val"]//text()')

        specifications_loader = fridge_loader.nested_css(':nth-child(6) tr')
        specifications_loader.add_css('altura', './/*[text()[contains(.,"Altura")]]/../td[@class="table-val"]//text()')
        specifications_loader.add_css('largura', './/*[text()[contains(.,"Largura")]]/../td[@class="table-val"]//text()')
        specifications_loader.add_css('profundidade', './/*[text()[contains(.,"Profundidade")]]/../td[@class="table-val"]//text()')
        specifications_loader.add_css('peso', './/*[text()[contains(.,"Peso")]]/../td[@class="table-val"]//text()')
        specifications_loader.add_css('voltagem', './/*[text()[contains(.,"Tensão / Voltagem")]]/../td[@class="table-val"]//text()')
        specifications_loader.add_css('consumo', './/*[text()[contains(.,"Consumo")]]/../td[@class="table-val"]//text()')

        yield fridge_loader.load_item()
