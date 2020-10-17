import logging
import sys

__all__ = ["LOGGER"]


def initLogger():
    logger = logging.getLogger("urlshortener")

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    console.setFormatter(formatter)

    logger.addHandler(console)
    return logger


LOGGER = initLogger()
