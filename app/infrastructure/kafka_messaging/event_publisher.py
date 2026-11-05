import json
from typing import Any

from aiokafka import AIOKafkaProducer

from app.application.ports.messaging.event_publisher import EventPublisher


class KafkaEventPublisher(EventPublisher):
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def publish(
        self, topic: str, message: dict[str, Any], key: str | None = None
    ) -> None:
        value = json.dumps(message).encode("utf-8")
        encoded_key = key.encode("utf-8") if key is not None else None

        await self.producer.send_and_wait(topic=topic, value=value, key=encoded_key)
