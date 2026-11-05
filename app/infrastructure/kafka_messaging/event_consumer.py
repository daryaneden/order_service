import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka import AIOKafkaConsumer

from app.application.exceptions import OrderNotFoundException

logger = logging.getLogger(__name__)

EventHandler = Callable[[dict[str, Any], str, int, int], Awaitable[None]]

class KafkaEventConsumer:

    def __init__(self, topic: str, bootstrap_servers: str, group_id: str):

        self.consumer = AIOKafkaConsumer(topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest")

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()

    async def consume(self, handler: EventHandler) -> None:
        async for message in self.consumer:
            try:
                payload = json.loads(message.value)

                await handler(payload,
                    message.topic,
                    message.partition,
                    message.offset)

                await self.consumer.commit()

            except OrderNotFoundException as error:
                logger.warning("Order not found while processing Kafka message. "
                    "Message will be skipped: topic=%s, partition=%s, "
                    "offset=%s, error=%s",
                    message.topic,
                    message.partition,
                    message.offset,
                    error)

                await self.consumer.commit()

            except Exception:
                logger.exception("Failed to process Kafka message: topic=%s, partition=%s, offset=%s",
                    message.topic,
                    message.partition,
                    message.offset)
                raise
