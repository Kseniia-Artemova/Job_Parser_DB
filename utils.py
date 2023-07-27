import logging
from logging.handlers import RotatingFileHandler


def basic_logger(msg, level=logging.INFO, encoding="UTF-8"):
    format = "%(asctime)s %(levelname)s %(message)s"
    try:
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        handler = RotatingFileHandler('logs/query_log.log',
                                      maxBytes=100_000,
                                      backupCount=1,
                                      encoding=encoding)
        handler.setFormatter(logging.Formatter(format))
        logger.addHandler(handler)
        logger.info(f"Query:{msg}")

    except PermissionError as error:
        pass

    except Exception as error:
        print(f"\033[31mОшибка логирования: {error}\033[0m")