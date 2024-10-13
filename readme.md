## Web scraper with Celery, Scrapy and ELK stack

The server is using FastApi for api management. The scraping is done using distributed tasks using celery. Each celery worker runs scrapy tasks for the web scraping part.

The extracted data is indexed in elasticsearch at the end of each task.

Monitoring is realised using opentelemetry and loguru for logging and tracing.
Logs are stored using Logstash and the traces are collected using otel-collector and APM server.

## Run locally

1. Use the root of the repo as your working dir
2. Use docker compose up --build to start and build the containers
3. `Optional` First time buiding kibana, you have to configure the apm server manually by navigating in the left bar to APM and enable default integration. You do not have to enable elastic agent integration.
4. If you have not encountered any errors, you should be able to access your services

## Crawling, Indexing and Searching

* For starting the crawling from the list of website, use `POST` at localhost:8080/crawl-async with body `{'number_of_domains': int}`. The tasks are done in background and you can check the indexing using the index `scrapped_data` in kibana to view the data as it is added.

* For checking the time a crawl took, you can go in kibana to APM -> services -> server_app and check the last traces. You can see how many tasks were, if any errors were encountered and the total time taken.

* Searching is done with `GET` at localhost:8080/query-index with query parameters:
`name: Optional[str]
url: Optional[str]
phone_number: Optional[str] 
social_media_links: Optional[str] 
facebook: Optional[str] 
addresses: Optional[str] `. You will receive the most appropiate result if there is any based on your parameters. The querying has to be done after populating the index by crawling.


