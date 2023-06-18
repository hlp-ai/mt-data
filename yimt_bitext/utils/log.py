import logging
from logging.handlers import RotatingFileHandler


def get_logger(log_filename="./logs/crawl.log", name="mt.data"):
    """Get a logger with RotatingFileHandler and StreamHandler with DEBUG level"""
    logger = logging.getLogger(name)
    # fn = "{}.log".format(log_filename)
    formatter = logging.Formatter("%(asctime)s - %(name)s-%(levelname)s %(message)s")

    max_bytes = 64*1024*1024
    fh = RotatingFileHandler(log_filename, maxBytes=max_bytes, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)

    logger.setLevel(logging.DEBUG)

    return logger
