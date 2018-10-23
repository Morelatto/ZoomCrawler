# -*- coding: utf-8 -*-
import scrapy

from zoom.items import WasherLoader


class ZoomWasherSpider(scrapy.Spider):
    name = 'zoom_washers'

    start_urls = ['https://www.zoom.com.br/lavadora-roupas/preco-ate-1000']

    def parse(self, response):
        for washer_link in response.css('.tp-default .name-link::attr(href)').extract():
            yield scrapy.Request('https://www.zoom.com.br' + washer_link, callback=self.parse_washer)

        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page not in (None, 'javascript:void(0);'):
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @classmethod
    def parse_washer(cls, response):
        washer_loader = WasherLoader(selector=response.css('.tech-spec-table tbody'))
        washer_loader.add_xpath('nome', '//h1[@class="product-name"]/span/text()')
        washer_loader.add_xpath('rating', '//div[@class="rating"]/span/@class')
        washer_loader.add_xpath('avaliacoes', '//a[@class="vote-txt"]/span/text()')
        washer_loader.add_xpath('preco', '//a[@class="price-label"]/strong/text()')

        basic_info_loader = washer_loader.nested_css(':nth-child(1) tr')
        basic_info_loader.add_xpath('marca', './/*[text()[contains(.,"Marca")]]/../td[@class="table-val"]//text()')
        basic_info_loader.add_xpath('modelo', './/*[text()[contains(.,"Modelo")]]/../td[@class="table-val"]//text()')

        details_loader = washer_loader.nested_css(':nth-child(2) tr')
        details_loader.add_xpath('tipo', './/*[text()[contains(.,"Tipo")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('abertura', './/*[text()[contains(.,"Abertura da tampa")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('capacidade', './/*[text()[contains(.,"Capacidade de Lavagem")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('controle', './/*[text()[contains(.,"Controle")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('recursos_avancados', './/*[text()[contains(.,"Recursos Avançados")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('programas', './/*[text()[contains(.,"Quantidade de Programas de Lavagem")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('acabamento_gabinete', './/*[text()[contains(.,"Acabamento do Gabinete")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('acabamento_cesto', './/*[text()[contains(.,"Acabamento do Cesto")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('operacoes', './/*[text()[contains(.,"Operações da Lavadora")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('velocidade', './/*[text()[contains(.,"Velocidade de Centrifugação")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('enxagues', './/*[text()[contains(.,"Quantidade de Enxágues")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('dispenser', './/*[text()[contains(.,"Dispenser Para")]]/../../td[@class="table-val"]//text()')
        details_loader.add_xpath('recursos_basicos', './/*[text()[contains(.,"Recursos Básicos")]]/../../td[@class="table-val"]//text()')

        resources_loader = washer_loader.nested_css(':nth-child(3) tr')
        resources_loader.add_xpath('eficiencia_energetica', './/*[text()[contains(.,"Eficiência Energética")]]/../../td[@class="table-val"]//text()')
        resources_loader.add_xpath('eco_lavagem', './/*[text()[contains(.,"Eco Lavagem")]]/../../td[@class="table-val"]//text()')
        resources_loader.add_xpath('economia_agua', './/*[text()[contains(.,"Economia de Água")]]/../../td[@class="table-val"]//text()')
        resources_loader.add_xpath('reaproveitamento_agua', './/*[text()[contains(.,"Reaproveitamento de Água")]]/../../td[@class="table-val"]//text()')

        specifications_loader = washer_loader.nested_css(':nth-child(5) tr')
        specifications_loader.add_xpath('altura', './/*[text()[contains(.,"Altura")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('largura', './/*[text()[contains(.,"Largura")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('profundidade', './/*[text()[contains(.,"Profundidade")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('peso', './/*[text()[contains(.,"Peso")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('voltagem', './/*[text()[contains(.,"Voltagem")]]/../../td[@class="table-val"]//text()')
        specifications_loader.add_xpath('consumo', './/*[text()[contains(.,"Consumo")]]/../../td[@class="table-val"]//text()')

        yield washer_loader.load_item()
