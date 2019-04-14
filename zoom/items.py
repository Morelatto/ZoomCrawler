# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import Compose, TakeFirst, Join


def get_last(l):
    return l.split()[-1] if l is not None and len(l) > 0 else None


parse_rating = Compose(TakeFirst(), lambda css_classes: css_classes.split()[-1].replace('star_', ''))
remove_currency = Compose(TakeFirst(), get_last)


class Fridge(scrapy.Item):
    nome = scrapy.Field()
    rating = scrapy.Field()
    preco = scrapy.Field()
    marca = scrapy.Field()
    modelo = scrapy.Field()
    capacidade_total = scrapy.Field()
    capacidade_refrigerador = scrapy.Field()
    capacidade_freezer = scrapy.Field()
    tipo_porta = scrapy.Field()
    recursos_especiais_refrigerador = scrapy.Field()
    recursos_basicos_refrigerador = scrapy.Field()
    dispenser_externo = scrapy.Field()
    tipo_controle = scrapy.Field()
    acabamento_porta = scrapy.Field()
    material_prateleira = scrapy.Field()
    recursos_freezer = scrapy.Field()
    tipo_degelo = scrapy.Field()
    eficiencia_energetica = scrapy.Field()
    altura = scrapy.Field()
    largura = scrapy.Field()
    profundidade = scrapy.Field()
    peso = scrapy.Field()
    voltagem = scrapy.Field()
    consumo = scrapy.Field()


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
    avaliacoes = scrapy.Field()
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
    eficiencia_energetica = scrapy.Field()
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


class Washer(scrapy.Item):
    nome = scrapy.Field()
    rating = scrapy.Field()
    avaliacoes = scrapy.Field()
    preco = scrapy.Field()
    marca = scrapy.Field()
    modelo = scrapy.Field()
    tipo = scrapy.Field()
    abertura = scrapy.Field()
    capacidade = scrapy.Field()
    controle = scrapy.Field()
    recursos_avancados = scrapy.Field()
    programas = scrapy.Field()
    acabamento_gabinete = scrapy.Field()
    acabamento_cesto = scrapy.Field()
    operacoes = scrapy.Field()
    velocidade = scrapy.Field()
    enxagues = scrapy.Field()
    dispenser = scrapy.Field()
    recursos_basicos = scrapy.Field()
    eficiencia_energetica = scrapy.Field()
    eco_lavagem = scrapy.Field()
    economia_agua = scrapy.Field()
    reaproveitamento_agua = scrapy.Field()
    altura = scrapy.Field()
    largura = scrapy.Field()
    profundidade = scrapy.Field()
    peso = scrapy.Field()
    voltagem = scrapy.Field()
    consumo = scrapy.Field()


class WasherLoader(ItemLoader):
    default_item_class = Washer
    default_output_processor = TakeFirst()

    rating_out = parse_rating
    controle_out = Identity()
    operacoes_out = Identity()
    dispenser_out = Identity()
    recursos_basicos_out = Identity()
    recursos_avancados_out = Identity()
    voltagem = Identity()


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
