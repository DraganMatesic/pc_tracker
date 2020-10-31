import json
import logging
from logging.handlers import RotatingFileHandler


def json_serial(object_):
    try:
        return object_.__dict__
    except AttributeError:
        return str(object_)


class JsonFormater(logging.Formatter):
    def format(self, record):
        return json.dumps(record.__dict__.get('args'), default=json_serial)


def history_logger_simple(history_log_path):
    formatter = JsonFormater()
    json_handler = RotatingFileHandler(filename=history_log_path, maxBytes=1024*1024, backupCount=1000)
    json_handler.setFormatter(formatter)

    history_logger = logging.getLogger('history_json')
    history_logger.addHandler(json_handler)
    history_logger.setLevel(logging.INFO)
    return history_logger
