from collections.abc import Awaitable, Callable
from typing import Any
import json
import logging

from aiokafka import AIOKafkaConsumer

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

                logger.info(
                    "Kafka message received: topic=%s, partition=%s, offset=%s, payload=%s",
                    message.topic,
                    message.partition,
                    message.offset,
                    payload,
                )

                await handler(
                    payload,
                    message.topic,
                    message.partition,
                    message.offset,
                )

                await self.consumer.commit()

            except Exception:
                logger.exception(
                    "Failed to process Kafka message: topic=%s, partition=%s, offset=%s",
                    message.topic,
                    message.partition,
                    message.offset,
                )
                raise