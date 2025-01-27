import asyncio
import json
import logging
import time
from datetime import datetime

import aio_pika
from aio_pika import ExchangeType
from requests import Request


class LoggerProvider:

    connection: aio_pika.robust_connection = None
    channel : aio_pika.channel= None
    exchange_name = None
    exchange : aio_pika.robust_exchange = None
    rabbitmq_host = None
    rabbitmq_user = None
    rabbitmq_password = None
    logger : logging.Logger = None

    @classmethod
    async def create(cls, rabbitmq_host, rabbitmq_user, rabbitmq_password, logger: logging.Logger):
        self=LoggerProvider()
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_password = rabbitmq_password
        self.logger = logger
        await self.subscribe_channel()
        return self


    async def subscribe_channel(self):
        retries = 5
        for attempt in range(retries):
            try:
                self.connection = await aio_pika.connect_robust(
                    host=self.rabbitmq_host,
                    virtualhost='/',
                    login=self.rabbitmq_user,
                    password=self.rabbitmq_password
                )
            except Exception as e:
                self.logger.error(f"Connection failed: {e}")
                if attempt < retries - 1:
                    self.logger.info(f"Retrying in {5} seconds...")
                    await asyncio.sleep(5)
                else:
                    self.logger.error("All retry attempts failed")
        self.logger.info("Connection established")
        self.logger.info("Connected to RabbitMQ")
        self.channel = await self.connection.channel()
        self.logger.info("Channel created")
        self.exchange_name = 'log'
        self.logger.info("Exchange created")
        self.exchange = await self.channel.declare_exchange(name=self.exchange_name, type=ExchangeType.TOPIC, durable=True)
        
    @staticmethod    
    async def log_request(request:Request, app_logger: logging.Logger):
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
    
        app_logger.info("Received request", extra={"data": extra_info})


    async def send_warning_log(self, key,message):
        data={
            "key": key,
            "log_level": "warning",
            "message": message,
            "timestamp":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }
        message_body = json.dumps(data)
        await self.publish(message_body, "warning")
        
    async def send_info_log(self, key,message):
        data={
            "key": key,
            "log_level": "information",
            "message": message,
            "timestamp":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }
        message_body = json.dumps(data)
        await self.publish(message_body, "info")

    async def send_error_log(self, key,message):
        data={
            "key": key,
            "log_level": "error",
            "message": message,
            "timestamp":time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        }
        message_body = json.dumps(data)
        await self.publish(message_body, "error")

    async def publish(self,message_body, routing_key):
        self.logger.info("Publishing message to exchange %s with routing key %s", self.exchange_name, routing_key)
        await self.exchange.publish(
            aio_pika.Message(
                body=message_body.encode(),
                content_type="text/plain"
            ),
            routing_key=routing_key)