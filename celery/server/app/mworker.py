from typing import List
from celery import Celery

from app.config import message_broker, redis_url

app = Celery(
    'crawler_queue',
    broker="amqp://" + message_broker,
    backend="redis://" + redis_url + "/0",
    CELERY_BROKER_HEARTBEAT=0
)

# app.conf.task_routes = {
#     'crawl_task': {'queue': 'crawler_queue'},
#     'index_crawl_data': {'queue': 'crawler_queue_index'},
#     'crawl_task_callback': {'queue': 'crawler_queue'}
# }


class CeleryConfig:
    task_serializer = "json"
    result_serializer = "json"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]


app.config_from_object(CeleryConfig)

@app.task(name="crawl_task")
def test(url: List[str]):
    pass

@app.task(name="index_crawl_data")
def index_crawl_data(data: List[dict]):
    pass

@app.task(name="crawl_task_callback")
def crawl_task_callback():
    pass
