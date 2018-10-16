from scrapy import cmdline

cmdline.execute("scrapy crawl zoom_ovens -o results.csv".split())
