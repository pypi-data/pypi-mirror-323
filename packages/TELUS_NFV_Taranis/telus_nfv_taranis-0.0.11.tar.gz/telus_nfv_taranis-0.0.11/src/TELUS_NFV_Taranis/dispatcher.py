import asyncio
import logging
from nats.aio.client import Client as NATS
from nats.js.api import ConsumerConfig
from typing import Callable, Awaitable

class Dispatcher:
    def __init__(self, nats_url: str, nats_token: str):
        self.nc = NATS()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.nats_url = nats_url
        self.nats_token = nats_token
        self.handlers: dict[str, Callable[[str], Awaitable[None]]] = {}

    def register_handler(self, subject: str, handler: Callable[[str], Awaitable[None]]):
        self.handlers[subject] = handler

    async def message_router(self, msg):
        subject = msg.subject
        data = msg.data.decode()
        self.logger.debug(f"Received message on subject {subject} with data: \n{data}")

        if subject in self.handlers:
            handler = self.handlers[subject]
            await handler(msg)
        else:
            raise Exception(f"No handler registered for subject: {subject}")

    async def validate_message(self, data, model_class):
        try:
            return model_class.model_validate_json(data)
        except Exception as e:
            self.logger.info(f"Failed to validate message with error: {e}")
            return None

    async def run(self):
        
        nats_url = self.nats_url
        nats_token = self.nats_token
        await self.nc.connect(
            servers=[nats_url],
            token=nats_token
        )
        js = self.nc.jetstream()
        
        config = ConsumerConfig(deliver_policy="new")

        subjects = self.handlers.keys()

        for subject in subjects:
            await js.subscribe(subject, cb=self.message_router, config=config)

        # Prevent the script from exiting
        await asyncio.Event().wait()  # Keeps the subscriber running indefinitely