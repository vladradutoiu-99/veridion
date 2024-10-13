import logging
import re

import scrapy
from scrapy import Request
from twisted.internet.error import DNSLookupError

from app.utils.logging_module.logger import logger

class MySpider(scrapy.Spider):
    name = 'scrap_spider'
    max_url_depth = 1
    
    def __init__(self, start_urls, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        
        self.logger.setLevel(logging.DEBUG)  # Set the logger level


    def start_requests(self):
        for url in self.start_urls:
            # Check for scheme in URL
            if not url.startswith('https'):
                yield Request('https://' + url, self.parse, errback=self.parse_error)
            if not url.startswith('http'):
                yield Request('http://' + url, self.parse, errback=self.parse_error)
            
    def parse_error(self, failure):
        logger.error(f"Error occurred: {failure.request.url}")
        if failure.check(DNSLookupError):
            request: Request = failure.request
            yield {
                'URL': request.url,
                'Status': "DNSLookupError"
            }
        else:
            request: Request = failure.request
            yield {
                'URL': request.url,
                'Status': "UnknownError"
            }
        
    def parse(self, response: Request):
        phone_numbers = response.xpath('//text()[re:test(., "\(?\+?\d{0,2}\)?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}")]/text()').extract()
        phone_numbers = [num.strip() for num in phone_numbers if re.match(r"\(?\+?\d{0,2}\)?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}", num.strip())]

        social_media_links = response.css('a::attr(href)').re(r'(https?://(?:www\.)?(?:facebook|twitter|instagram|linkedin|tiktok|snapchat)\.(?:com|net)/[^\s]+)')

        addresses = response.xpath('//text()[re:test(., "\d{1,5}\s\w+(\s\w+)*,\s?\w+(\s\w+)*")]').extract()
        addresses = [address.strip() for address in addresses if re.match(r'\d{1,5}\s\w+(\s\w+)*,\s?\w+(\s\w+)*', address.strip())]
        
        # logger.debug(f"Scrapped data: {phone_numbers}, {social_media_links}, {addresses} from {response.url}")

        yield {
            'URL': response.url,
            'phone_numbers': phone_numbers,
            'social_media_links': social_media_links,
            'addresses': addresses,
            'Status': "Success"
        }
        
        url_depth = response.url.count('/') - response.url.count('//') - 1  # Adjust for protocol (http/https)
        
        if url_depth < self.max_url_depth:
            next_pages = response.xpath('//a[contains(text(), "Next") or contains(text(), "Older") or contains(text(), "More") or contains(text(), "Continue") or re:test(., "\d+")]')
        
            for next_page in next_pages:
                next_page_url = next_page.xpath('@href').get()
                if next_page_url:
                    if not next_page_url.startswith(('http://', 'https://')):
                        next_page_url = response.urljoin(next_page_url)
                    
                    yield response.follow(next_page_url, self.parse)