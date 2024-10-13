
from celery import Celery, Task
from celery.signals import worker_process_init
from typing import List

from app.config import message_broker, redis_url
import app.utils.logging_module
from opentelemetry import trace

from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals

from app.restschema import CrawlResponse, CrawlingStatus
from app.spider import MySpider
from app.utils.elastic import ElasticSearch
from app.parser import Parser
from app.utils.tracer import initialize_tracer_with_instrumentation

from app.utils.logging_module.logger import logger

es = ElasticSearch()
parser = Parser("app/sample-websites-company-names.csv")

@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    initialize_tracer_with_instrumentation("crawler-worker")

app = Celery(
    'crawler_queue',
    broker="amqp://" + message_broker,
    backend="redis://" + redis_url + "/0",
    CELERY_BROKER_HEARTBEAT=0
)

def add_additional_data_to_response(response: CrawlResponse):
    response = parser.add_data(response)
    return response

@app.task(bind=True, name="crawl_task")
def test(self: Task, url: List[str]):
    
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("celery_task_processing"):
        scraped_data = []

        def collect_item(item, response, **kwargs):
            scraped_data.append(item)

        process = CrawlerProcess()
        dispatcher.connect(collect_item, signal=signals.item_scraped)

        process.crawl(MySpider, start_urls=url)
        process.start(stop_after_crawl=True)
        
        return scraped_data

@app.task(bind=True, name="index_crawl_data")
def index_crawl_data(self: Task, data: List[dict]):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("celery_task_indexing"):
        with logger.contextualize():
            for response in data:
                response = CrawlResponse.model_validate(response)
                if response.Status == CrawlingStatus.Success:
                    response = add_additional_data_to_response(response)

                logger.debug(f"Response: {response}")

                es.index_data(index="scrapped_data", data=response)
            
            return "Data indexed successfully"

@app.task(bind=True, name="crawl_task_callback")
def crawl_task_callback():
    return "Task Completed"
    