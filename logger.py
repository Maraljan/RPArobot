import sys
import logging


LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = '%(asctime)s %(levelname)-7s %(name)-15s: %(message)s'

LOG_BASE_NAME = 'robot'


def configure(level: str, root_level: str):
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger('')
    root_logger.addHandler(handler)
    root_logger.setLevel(root_level)

    robot_log = logging.getLogger(LOG_BASE_NAME)
    robot_log.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'{LOG_BASE_NAME}.{name}')
