import logging

import scrapy
from scrapy import Request
from twisted.internet.error import DNSLookupError

from utils import get_logger

logger = get_logger("scrapy_logger")

class MySpider(scrapy.Spider):
    name = 'scrap_spider'
    
    def __init__(self, start_urls, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        
        self.logger.setLevel(logging.DEBUG)  # Set the logger level


    def start_requests(self):
        for url in self.start_urls:
            # Check for scheme in URL
            if not url.startswith('https'):
                url = 'https://' + url
            
            yield Request(url, self.parse, errback=self.parse_error)
            
    def parse_error(self, failure):
        if failure.check(DNSLookupError):
            request: Request = failure.request
            yield {
                'URL': request.url,
                'Status': failure.value
            }
        
    def parse(self, response: Request):
        # logger.debug(response.url)
        # logger.debug(response.headers)
        for title in response.css('.oxy-post-title'):
            yield {'title': title.css('::text').get()}

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)