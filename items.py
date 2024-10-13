import scrapy

class MyItem(scrapy.Item):
    title = scrapy.Field()
    URL = scrapy.Field()
    Status = scrapy.Field()