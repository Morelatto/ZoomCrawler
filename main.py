from scrapy import cmdline

cmdline.execute("scrapy crawl zoom -o results.csv".split())
