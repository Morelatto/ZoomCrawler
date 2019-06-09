# -*- coding: utf-8 -*-
from scrapy_mongodb import MongoDBPipeline
from zoom.items import PriceHistory, ProductItem, TechSpecTable, UserRating


# TODO /etc/mongodb.conf
class MongoDBCollectionsPipeline(MongoDBPipeline):
    mapping = {
        ProductItem: 'products',
        PriceHistory: 'price_history',
        TechSpecTable: 'tech_spec_table',
        UserRating: 'user_rating',
    }

    def __init__(self, **kwargs):
        super(MongoDBCollectionsPipeline, self).__init__(**kwargs)
        self.collections = {}
        self.current_item_class = None  # wont work with buffers

    def open_spider(self, spider):
        super(MongoDBCollectionsPipeline, self).open_spider(spider)
        for item, collection_name in self.mapping.items():
            self.collections[item] = self.database[collection_name]

    def process_item(self, item, spider):
        self.current_item_class = item.__class__
        super(MongoDBCollectionsPipeline, self).process_item(item, spider)

    def get_collection(self, name):
        return self.mapping[self.current_item_class], self.collections[self.current_item_class]

    def export_item(self, item):
        pass
