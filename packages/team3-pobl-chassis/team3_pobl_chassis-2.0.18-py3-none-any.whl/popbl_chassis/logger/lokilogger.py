import json
import logging
from logging.config import dictConfig
from multiprocessing import Queue

from logging_loki import LokiQueueHandler

class JsonPassThroughFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "message": record.getMessage(),
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
        }

        if hasattr(record, 'data'):
            data_dict = json.loads(record.data)
            filtered_data = {k: v for k, v in data_dict.items() if k not in ['filename']}
            log_record.update(filtered_data)

        return json.dumps(log_record)
    
class LokiLogger:

    @classmethod
    async def create(cls):
        self = LokiLogger()
        return self

    @staticmethod
    def create_handler(app_name, app_env, loki_host):
        loki_handler = LokiQueueHandler(
            Queue(),
            url=f"http://{loki_host}:3100/loki/api/v1/push",
            tags={"app": app_name, "env": app_env},
            version="1",
        )
        return loki_handler

    @staticmethod
    def setup_logging(loki_handler: LokiQueueHandler, formatter_cls):
        # Asegurar que formatter_cls es una clase y no una instancia
        logging_config = {
            "version": 1,
            "formatters": {
                "json": {
                    "()":  formatter_cls
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "DEBUG",
                },
                "loki": {
                    "()": lambda: loki_handler,  # Esto puede ser simplemente "loki_handler" si la instancia ya está creada
                    "formatter": "json",
                    "level": "INFO",
                }
            },
            "loggers": {
                "app_logger": {
                    "level": "DEBUG",
                    "handlers": ["console", "loki"],
                    "propagate": False
                }
            }
        }
        dictConfig(logging_config)
        return logging.getLogger("app_logger")



    @staticmethod
    def setup_default_logging(loki_handler: LokiQueueHandler):
        logging_config = {
            "version": 1,
            "formatters": {
                "json_pass_through": {
                    "()": JsonPassThroughFormatter,  # Usa la clase directamente, sin instanciarla aquí.
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json_pass_through",
                    "level": "DEBUG",
                },
                "loki": {
                    "()": lambda: loki_handler,
                    "formatter": "json_pass_through",
                    "level": "INFO",
                }
            },
            "loggers": {
                "app_logger": {
                    "level": "DEBUG",
                    "handlers": ["console", "loki"],
                    "propagate": False
                }
            }
        }
        dictConfig(logging_config)
        return logging.getLogger("app_logger")