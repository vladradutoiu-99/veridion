from celery import group, chain, chord
from datetime import datetime

from fastapi import FastAPI, status, HTTPException, Query, Depends, Request
from typing import Optional, Annotated
from opentelemetry import trace
from app.mworker import test, index_crawl_data, crawl_task_callback

from app.parser import Parser
from app.utils.elastic import ElasticSearch
from app.restschema import CrawlingRequest, QueryUrl
from app.dependency_injection import get_query_params
from app.api.builder import api_base_builder

from app.api.logger import logger

es = ElasticSearch()

app = (
    api_base_builder
    .with_celery_publisher()
    .build()
)

@app.post("/crawl", status_code=status.HTTP_200_OK, include_in_schema=False)
def func(content: CrawlingRequest):
    
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("service_request"):
        parser = Parser('app/sample-websites.csv')

        df = parser.parse()

        domain_names = df['domain'].values.tolist()
        if content.number_of_domains:
            tasks_chains = []
            # for d in domain_names[0:content.number_of_domains]:
            #     tasks_chains.append(chain(test.s(d), index_crawl_data.s()))

            # create a list of groups of 20 domains from the list of domain names
            domain_names = [domain_names[i:i + 50] for i in range(0, len(domain_names[0:content.number_of_domains]), 50)]

            for d in domain_names:
                tasks_chains.append(chain(test.s(d), index_crawl_data.s()))
                
            result = group(tasks_chains)()

        result = result.get()
        
        logger.debug(f"Task Result: {result}")
        
        return result
    
@app.post("/crawl-async", status_code=status.HTTP_200_OK, include_in_schema=False)
def func(content: CrawlingRequest):
    
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("service_request"):
        parser = Parser('app/sample-websites.csv')

        df = parser.parse()

        domain_names = df['domain'].values.tolist()
        if content.number_of_domains:
            tasks_chains = []
            domain_names = [domain_names[i:i + 20] for i in range(0, len(domain_names[0:content.number_of_domains]), 20)]

            for d in domain_names:
                tasks_chains.append(chain(test.s(d), index_crawl_data.s()))
                
            # for d in domain_names[0:content.number_of_domains]:
            #     tasks_chains.append(chain(test.s(d), index_crawl_data.s()))
                
            chord(tasks_chains)(crawl_task_callback.si())

        return "Task Started"

@app.get("/query-index/", status_code=status.HTTP_200_OK)
def query(
    request: Request,
    # user_request: Annotated[QueryUrl, Depends(get_query_params)]
    user_request: QueryUrl = Depends(get_query_params)
):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("service_query_request"):
        logger.debug(f"Request method: {request.method}")
        try:
            logger.debug(f"Query Request: {user_request}")
            response = es.query(user_request)

            response = response['hits']['hits'][0:1]
            return response
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
@app.get("/query-all/", status_code=status.HTTP_200_OK)
def query_all():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("service_query_all_request"):
        try:
            response = es.query_all()
            
            return response
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")