# ZoomCrawler

Download products from [Zoom](https://zoom.com.br/) based on category or subcategory and store in MongoDB.

Collected information:
- [x] Product details
- [x] Offers from product
- [x] Price history
- [x] User rating and comments

## Requirements
* [Scrapy](https://github.com/scrapy/scrapy)
* [scrapy-mongodb](https://github.com/sebdah/scrapy-mongodb)
* [pymongo](https://github.com/mongodb/mongo-python-driver)
* [requests](https://github.com/kennethreitz/requests)
* [docopt](https://github.com/docopt/docopt)

## Usage
```
  zoom.py <category>...
  zoom.py --list-categories | --list-subcategories
  zoom.py -h | --help | --version
```

## Arguments
```
  <category>...         Category or subcategory names to filter.
```

## Options
```
  --list-categories     List all product categories.
  --list-subcategories  List all product sub categories.
  -h, --help            Show help message.
  --version             Show version.
 ```

## No MongoDB
To run without Mongo comment the following lines in settings.py:
```
ITEM_PIPELINES = {
    'zoom.pipelines.MongoDBCollectionsPipeline': 300,
}

MONGODB_DATABASE = 'zoom'
MONGODB_ADD_TIMESTAMP = True
MONGODB_UNIQUE_KEY = 'name'
```

Optionally, to save results to file, add to settings.py:
```
FEED_URI = 'zoom_results.json'
FEED_EXPORT_ENCODING = 'utf-8'
```