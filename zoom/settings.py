# -*- coding: utf-8 -*-
BOT_NAME = 'zoom'

SPIDER_MODULES = ['zoom.spiders']
NEWSPIDER_MODULE = 'zoom.spiders'

USER_AGENT = \
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_DEBUG = True

TELNETCONSOLE_ENABLED = False
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

ITEM_PIPELINES = {
    'zoom.pipelines.MongoDBCollectionsPipeline': 300,
}

MONGODB_DATABASE = 'zoom'
MONGODB_ADD_TIMESTAMP = True
MONGODB_UNIQUE_KEY = 'name'

# LOG_LEVEL = 'INFO'
