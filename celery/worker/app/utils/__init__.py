import logging 
import sys
import socket
import json
from os import environ

logstash_url = environ["LOGSTASH_URL"]
logstash_port = environ["LOGSTASH_LOG_PORT"]


RESET_COLOR = "\033[0m"
LOG_COLORS = {
    "DEBUG": "\033[94m",    # Blue
    "INFO": "\033[92m",     # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",    # Red
    "CRITICAL": "\033[95m"  # Magenta
}


class CustomFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""

    def format(self, record):
        log_level = record.levelname

        if log_level in LOG_COLORS:
            message = super().format(record)
            return LOG_COLORS[log_level] + message + RESET_COLOR
        else:
            return super().format(record)
        
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
            print("Sending log to Logstash")
            # log_entry = self.format(record)
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

def get_logger(logger_name):
    """Returns logger"""

    disable_scrapy_logs()
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.propagate = False  # Prevent messages from propagating to parent loggers
    
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'  # Define your timestamp format here
        
        formatter = CustomFormatter(log_format, datefmt=date_format)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
    logstash_handler = LogstashHandler(host=logstash_url, port=int(logstash_port))  # Adjust host/port as needed
    logstash_handler.setLevel(logging.DEBUG)
    
    logstash_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logstash_formatter = logging.Formatter(logstash_format, datefmt='%Y-%m-%d %H:%M:%S')
    logstash_handler.setFormatter(logstash_formatter)
    
    logger.addHandler(logstash_handler)
    
    return logger
    
logger = get_logger('scrapy_logger')
