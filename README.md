# ZoomCrawler

Download products from [Zoom](https://zoom.com.br/) based on category or subcategory and store in MongoDB.

Collected information:
- [x] Product details
- [x] Offers from product
- [ ] Price history
- [ ] User rating and comments

## Requirements
* [Python 3](https://www.python.org)
* [Scrapy](https://github.com/scrapy/scrapy)
* [scrapy-mongodb](https://github.com/sebdah/scrapy-mongodb) - optional
* [pymongo](https://github.com/mongodb/mongo-python-driver) - optional
* [docopt](https://github.com/docopt/docopt)

## Usage
```
  zoom.py <category_url>...
  zoom.py -h | --help | --version
```

## Arguments
```
  <category_url>...     List of category or subcategory urls to crawl. Ex.: tv/smart-tv tv
```

## Options
```
  -h, --help            Show help message.
  --version             Show version.
 ```

## MongoDB
Uncomment the following lines on settings.py to save results to a local MongoDB instance:
```
ITEM_PIPELINES = {
    'zoom.pipelines.MongoDBCollectionsPipeline': 300,
}

MONGODB_DATABASE = 'zoom'
MONGODB_ADD_TIMESTAMP = True
MONGODB_UNIQUE_KEY = 'name'
```

More information [here](https://github.com/sebdah/scrapy-mongodb).