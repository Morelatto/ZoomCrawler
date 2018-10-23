from scrapy import cmdline

cmdline.execute("scrapy crawl zoom_washers -o results.csv".split())
