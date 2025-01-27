import inspect
import json
import logging
from datetime import datetime
from popbl_chassis.logger.loglevel import LogLevel


class LokiLoggerProvider:
    
    @staticmethod
    async def log_request(request, app_logger: logging.Logger):
        headers = dict(request.headers)
        body_size = 0
        body_content = "No Content"

        try:
            body = await request.body()
            body_size = len(body)
            body_content = body.decode("utf-8")
        except Exception as e:
            app_logger.error("Failed to read body", exc_info=True)

        headers_size = sum(len(k) + len(v) for k, v in headers.items())
        packet_size = headers_size + body_size

        extra_info = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": request.client.host,
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "headers": json.dumps(headers),
            "body_size": body_size,
            "packet_size": packet_size,
            "body_content": body_content
        }
        
        json_extra_info=json.dumps(extra_info)

        app_logger.info("Request", extra={"data": json_extra_info})

    @staticmethod
    async def send_log(app_logger: logging.Logger, key, message, level: LogLevel=LogLevel.INFO):
        log_data = {
            "key": key,
            "message": message,
        }
    
        message_body = json.dumps(log_data)
    
        if level == LogLevel.DEBUG:
            app_logger.debug("Log", extra={"data": message_body})
        elif level == LogLevel.INFO:
            app_logger.info("Log", extra={"data": message_body})
        elif level == LogLevel.WARNING:
            app_logger.warning("Log", extra={"data": message_body})
        elif level == LogLevel.ERROR:
            app_logger.error("Log", extra={"data": message_body})
        elif level == LogLevel.CRITICAL:
            app_logger.critical("Log", extra={"data": message_body})
        else:
            raise ValueError(f"Invalid log level: {level}")
        
    @staticmethod
    async def log_response(app_logger: logging.Logger, key, message, level:LogLevel.INFO , status_code):
        log_data = {
            "key": key,
            "message": message,
            "status_code": status_code,
        }
        message_body = json.dumps(log_data)

        if level == LogLevel.INFO:
            app_logger.info("Log", extra={"data": message_body})
        elif level == LogLevel.WARNING:
            app_logger.warning("Log", extra={"data": message_body})
        elif level == LogLevel.ERROR:
            app_logger.error("Log", extra={"data": message_body})
