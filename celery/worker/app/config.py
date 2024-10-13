from os import environ

redis_url = environ["REDIS_URL"]
message_broker = environ["MESSAGE_BROKER"]
logstash_url = environ["LOGSTASH_URL"]
logstash_port = environ["LOGSTASH_LOG_PORT"]
