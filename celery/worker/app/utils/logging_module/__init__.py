import logging

from celery.signals import setup_logging

from app.utils import logger as scrapy_logger

import stackprinter

from loguru import logger

__stackprinter_kwargs = {            
    "reverse": True, 
    "suppressed_paths": [r"lib/python.*/site-packages/*"]
}

stackprinter.set_excepthook(**__stackprinter_kwargs)

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


def intercept_celery_logger(logger=None,loglevel=logging.DEBUG, **kwargs):
    handler = InterceptHandler()
    handler.setLevel(0)
    scrapy_logger.addHandler(handler)
    return scrapy_logger

setup_logging.connect(intercept_celery_logger)
