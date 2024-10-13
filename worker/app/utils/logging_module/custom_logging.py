import logging
from os import environ
import sys
import json
import stackprinter
import socket
from loguru import logger
from opentelemetry import trace

logstash_url = environ["LOGSTASH_URL"]
logstash_port = environ["LOGSTASH_LOG_PORT"]

__stackprinter_kwargs = {            
    "reverse": True, 
    "suppressed_paths": [r"lib/python.*/site-packages/*"]
}

stackprinter.set_excepthook(**__stackprinter_kwargs)

class LogstashHandler(logging.Handler):
    """Custom handler to send logs to Logstash via TCP."""
    
    def __init__(self, host, port):
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def emit(self, record):
        try:
            log_data = {
                "logger": record.name,
                "level": record.levelname,
                "message": record.getMessage(),
                "file": record.pathname,
                "line": record.lineno,
            }
            self.sock.sendall((json.dumps(log_data) + "\n").encode('utf-8'))
        except Exception:
            self.handleError(record)
    

class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind()
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level,record.getMessage())

def serialize(record):
    source_location = {
        "file": record["name"],
        "line": record["line"],
        "function": record["function"]
    }


    message = record["message"]
    exc = record["exception"]

    subset = {
        "severity": record["level"].name,
        "sourceLocation": source_location,
        **record["extra"]
    }
    
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, "x")

    subset["traceId"] = trace_id
    

    if exc:
        span.record_exception(exc)
        stack_trace = stackprinter.format(
            exc,
            **__stackprinter_kwargs
        )
        message = message
        subset["stack_trace"] = stack_trace

    subset["message"] = message

    return json.dumps(subset, default=str)

def formatter(record):
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"

def disable_scrapy_logs():
    """Disables Scrapy logs by setting its logger level to CRITICAL."""
    scrapy_logger = logging.getLogger('scrapy')
    scrapy_logger.setLevel(logging.CRITICAL)
    scrapy_logger.propagate = False
    
    logging.getLogger('scrapy.downloadermiddlewares.httpcompression').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.downloadermiddlewares.ssl').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.core.downloader.handlers.http11').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.core.engine').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.downloadermiddlewares.redirect').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.downloadermiddlewares.cookies').setLevel(logging.CRITICAL)
    logging.getLogger('scrapy.utils.ssl').setLevel(logging.CRITICAL)
    
    logging.getLogger('twisted').setLevel(logging.CRITICAL)  # Suppress Twisted logs
    
def disable_celery_logs():
    """Disables Celery logs by setting its logger level to CRITICAL."""
    celery_logger = logging.getLogger('celery.worker.consumer.gossip')
    celery_logger.setLevel(logging.CRITICAL)
    celery_logger.propagate = False
    
    logging.getLogger('celery.worker.strategy').setLevel(logging.CRITICAL)
    logging.getLogger('celery.worker.consumer').setLevel(logging.CRITICAL)
    logging.getLogger('amqp').setLevel(logging.CRITICAL)
    logging.getLogger('celery.bootsteps').setLevel(logging.CRITICAL)
    logging.getLogger('celery.utils.functional').setLevel(logging.CRITICAL)
    logging.getLogger('celery').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('kombu').setLevel(logging.CRITICAL)


class CustomizeLogger:

    @classmethod
    def make_logger(cls):
        logger = cls.customize_logging()

        return logger

    @classmethod
    def customize_logging(cls):
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler(level=40)]
        for _log in ['uvicorn',
                     'fastapi',
                     'celery',
                     'celery.task',
                     'socketio',
                     'engineio'
                    ]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        logger_dev_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        disable_scrapy_logs()
        disable_celery_logs()
        
        format = logger_dev_format
        logger.remove()
        logger.add(sys.stderr, format=format, level="TRACE", backtrace=True)
        logger.add(LogstashHandler(logstash_url, int(logstash_port)), level="TRACE", backtrace=True)

        return logger
