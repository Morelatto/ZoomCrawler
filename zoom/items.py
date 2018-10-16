# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader.processors import TakeFirst, Compose
from scrapy.loader import ItemLoader, Identity

parse_rating = Compose(TakeFirst(), lambda css_classes: css_classes.split()[-1].replace('star_', ''))


class Fridge(scrapy.Item):
    name = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    total_capacity = scrapy.Field()
    cooler_capacity = scrapy.Field()
    freezer_capacity = scrapy.Field()
    door = scrapy.Field()
    special_resources = scrapy.Field()
    basic_resources = scrapy.Field()
    external_dispenser = scrapy.Field()
    door_material = scrapy.Field()
    shelf_material = scrapy.Field()
    freezer_resources = scrapy.Field()
    defrost_type = scrapy.Field()
    energetic_efficiency = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    depth = scrapy.Field()
    weight = scrapy.Field()
    voltage = scrapy.Field()
    consumption = scrapy.Field()


class FridgeLoader(ItemLoader):
    default_item_class = Fridge
    default_output_processor = TakeFirst()

    rating_out = parse_rating
    special_resources_out = Identity()
    basic_resources_out = Identity()
    freezer_resources_out = Identity()
    voltage_out = Identity()


class Oven(scrapy.Item):
    nome = scrapy.Field()
    rating = scrapy.Field()
    preco = scrapy.Field()
    marca = scrapy.Field()
    modelo = scrapy.Field()
    tipo = scrapy.Field()
    bocas = scrapy.Field()
    funcionamento_mesa = scrapy.Field()
    acendimento_mesa = scrapy.Field()
    acabamento_inox = scrapy.Field()
    material_mesa = scrapy.Field()
    funcoes_mesa = scrapy.Field()
    tipo_grade = scrapy.Field()
    capacidade_forno = scrapy.Field()
    prateleiras_forno = scrapy.Field()
    funcoes_forno = scrapy.Field()
    funcoes_especiais_forno = scrapy.Field()
    energetic_efficiency = scrapy.Field()
    altura = scrapy.Field()
    largura = scrapy.Field()
    profundidade = scrapy.Field()
    peso = scrapy.Field()
    voltagem = scrapy.Field()


class OvenLoader(ItemLoader):
    default_item_class = Oven
    default_output_processor = TakeFirst()

    rating_out = parse_rating
    funcoes_mesa_out = Identity()
    prateleiras_forno_out = Identity()
    funcoes_forno_out = Identity()
    funcoes_especiais_forno_out = Identity()
    voltagem = Identity()
