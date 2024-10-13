from os import environ
from elasticsearch import Elasticsearch

from app.utils import get_logger
from app.restschema import CrawlResponse

logger = get_logger('elastic_logger')

ELASTIC_PASSWORD = environ["ELASTIC_PASSWORD"]
ELASTIC_URL = environ["ELASTIC_URL"]
ELASTIC_PORT = environ["ELASTIC_PORT"]
ELASTIC_USERNAME = environ["ELASTIC_USERNAME"]
ELASTIC_CERTS_DIR = environ["ELASTIC_CERTS_DIR"]

class ElasticSearch():
    def __init__(self):
        self.es = Elasticsearch(
            hosts=f"https://{ELASTIC_URL}:{ELASTIC_PORT}",
            ca_certs=f"{ELASTIC_CERTS_DIR}/ca/ca.crt",
            basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
        )
        
        logger.debug(f"Elasticsearch connection established {self.es.info()}")

    def index_data(self, index:str, data: CrawlResponse):
        self.es.index(index=index, body=data.__dict__)