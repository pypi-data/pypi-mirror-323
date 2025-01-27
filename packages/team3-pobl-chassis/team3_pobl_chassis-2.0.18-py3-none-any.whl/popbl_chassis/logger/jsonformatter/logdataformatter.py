import json
import logging
from datetime import time


class LogDataFormatter(logging.Formatter):
    def format(self, record):
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

        log_record = {
            "timestamp": created_time,
            "level": logging.getLevelName(record.levelno),  # Convertir nivel numérico a nombre
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName
        }

        # Agregar información de excepción si está presente
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_record)
