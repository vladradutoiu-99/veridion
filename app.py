from parser import Parser

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy import signals

from spider import MySpider

from twisted.internet import reactor


parser = Parser('sample-websites.csv')

df = parser.parse()

domain_names = df['domain'].values.tolist()

process = CrawlerProcess()

spider = MySpider(
    start_urls=domain_names[0:10]
)

dispatcher = process.signals
dispatcher.connect(spider.errback, signal=signals.spider_error)

d = process.crawl(spider)
d.addBoth(lambda _: reactor.stop())

process.start()

# crawler = process.crawl(MySpider, start_urls=domain_names[0:10])
# process.start()

