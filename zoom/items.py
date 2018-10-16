# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader.processors import TakeFirst
from scrapy.loader import ItemLoader, Identity


class Fridge(scrapy.Item):
    name = scrapy.Field()
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

    special_resources_out = Identity()
    basic_resources_out = Identity()
    freezer_resources_out = Identity()
    voltage_out = Identity()
