# pipelines.py
import logging

class LoggingPipeline:
    def open_spider(self, spider):
        spider.logger.info("Opening spider: %s", spider.name)

    def close_spider(self, spider):
        spider.logger.info("Closing spider: %s", spider.name)

    def process_item(self, item, spider):
        # Log the item or print it directly
        spider.logger.info("Item scraped: %s", item)
        return item