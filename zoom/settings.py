# -*- coding: utf-8 -*-
import pathlib

BOT_NAME = 'zoom'

SPIDER_MODULES = ['zoom.spiders']
NEWSPIDER_MODULE = 'zoom.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'

ROBOTSTXT_OBEY = False

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
AUTOTHROTTLE_DEBUG = True
# DUPEFILTER_DEBUG = True

TELNETCONSOLE_ENABLED = False
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# ITEM_PIPELINES = {
#     'zoom.pipelines.MongoDBCollectionsPipeline': 300,
# }

# MONGODB_DATABASE = 'zoom'
# MONGODB_ADD_TIMESTAMP = True
# MONGODB_UNIQUE_KEY = 'name'

LOG_LEVEL = 'INFO'

FEEDS = {
    pathlib.Path('items.csv'): {
        'format': 'csv',
    },
}
