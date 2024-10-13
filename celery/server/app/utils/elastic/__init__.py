from os import environ
from elasticsearch import Elasticsearch

from app.utils import get_logger
from app.restschema import QueryUrl

from app.api.logger import logger

ELASTIC_PASSWORD = environ["ELASTIC_PASSWORD"]
ELASTIC_URL = environ["ELASTIC_URL"]
ELASTIC_PORT = environ["ELASTIC_PORT"]
ELASTIC_USERNAME = environ["ELASTIC_USERNAME"]
ELASTIC_CERTS_DIR = environ["ELASTIC_CERTS_DIR"]

logger.info(f"Elastic cert dir: {ELASTIC_CERTS_DIR}")

index = "scrapped_data"

class ElasticSearch():
    def __init__(self):
        self.es = Elasticsearch(
            hosts=f"https://{ELASTIC_URL}:{ELASTIC_PORT}",
            ca_certs=f"{ELASTIC_CERTS_DIR}/ca/ca.crt",
            basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
        )
        
        logger.debug(f"Elasticsearch connection established {self.es.info()}")

    def query(self, query: QueryUrl, max_results:int = 10):

        def build_query_body(query: QueryUrl, max_results):
            should_clauses = []

            # Add fuzzy search for commercial name if not None
            if query.name is not None:
                should_clauses.append({
                    "fuzzy": {
                        "company_commercial_name": {
                            "value": query.name,
                            "fuzziness": "AUTO"
                        }
                    }
                })

            # Add fuzzy search for legal name if not None
            if query.name is not None:
                should_clauses.append({
                    "fuzzy": {
                        "company_legal_name": {
                            "value": query.name,
                            "fuzziness": "AUTO"
                        }
                    }
                })

            # Add fuzzy search for all available names if not None
            if query.name is not None:
                should_clauses.append({
                    "fuzzy": {
                        "company_all_available_names": {
                            "value": query.name,
                            "fuzziness": "AUTO"
                        }
                    }
                })

            # Add wildcard search for phone numbers if not None
            if query.phone_number is not None:
                should_clauses.append({
                    "wildcard": {
                        "phone_numbers": f"*{query.phone_number}*"
                    }
                })

            # Add fuzzy search for URL if not None
            if query.url is not None:
                should_clauses.append({
                    "fuzzy": {
                        "URL": {
                            "value": query.url.split('/')[2],
                            "fuzziness": "AUTO"
                        }
                    }
                })

            # Add fuzzy search for social media links if not None
            if query.facebook is not None:
                should_clauses.append({
                    "fuzzy": {
                        "social_media_links": {
                            "value": query.facebook,
                            "fuzziness": "AUTO"
                        }
                    }
                })

            # Construct the query body
            query_body = {
                "size": max_results,  # Limit the number of results
                "query": {
                    "bool": {
                        "should": should_clauses
                    }
                }
            }

            return query_body



        query_body = build_query_body(query, max_results)

        logger.debug(f"Query Body: {query_body}")

        return self.es.search(index=index, body=query_body, allow_partial_search_results=True)
    
    def query_all(self):
        return self.es.search(index=index, body={"query": {"match_all": {}}})