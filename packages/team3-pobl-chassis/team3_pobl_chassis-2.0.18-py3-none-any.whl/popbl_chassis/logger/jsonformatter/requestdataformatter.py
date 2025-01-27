import json
import logging
import time


class RequestDataFormatter(logging.Formatter):
    def format(self, record):
        data = getattr(record, 'data', {})
        def get_data(field, default='unknown'):
            return data.get(field, default)

        log_record = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
            "client_ip": get_data('client_ip'),
            "method": get_data('method'),
            "path": get_data('path'),
            "status_code": get_data('status_code'),
            "user_agent": get_data('user_agent'),
            "headers": get_data('headers'),
            "body_size": get_data('body_size'),
            "packet_size": get_data('packet_size'),
            "body_content": get_data('body_content'),
        }

        return json.dumps(log_record)
