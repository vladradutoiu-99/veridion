import logging
from app.utils.logging_module.custom_logging import CustomizeLogger

def setup_root_logger():
    logging.basicConfig(
        encoding="utf-8",
        level=logging.NOTSET,
        format="[%(name)s] - %(message)s"
    )


logger = CustomizeLogger.make_logger()