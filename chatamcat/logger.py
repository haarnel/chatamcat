import logging
from logging.handlers import SysLogHandler


def getLogger():
    logger = logging.getLogger("chatamcat")
    console = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="[ %(name)s ] [ %(levelname)s ] [ %(asctime)s ] %(message)s"
    )
    console.setFormatter(formatter)
    syslog = SysLogHandler(address="localhost")
    logger.addHandler(console)
    logger.addHandler(syslog)
    logger.setLevel(logging.INFO)
    return logger
