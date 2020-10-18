import logging

__all__ = ["LOGGER"]


def initLogger():
    logger = logging.getLogger("urlshortener")
    logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler()

    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    console.setFormatter(formatter)

    logger.addHandler(console)
    return logger


LOGGER = initLogger()  # a singleton logger for project use
