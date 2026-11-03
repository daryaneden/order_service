from contextlib import asynccontextmanager

from fastapi import FastAPI
import asyncio

from app.infrastructure.kafka_messaging.event_publisher import KafkaEventPublisher
from app.infrastructure.kafka_messaging.event_consumer import KafkaEventConsumer
from app.infrastructure.outbox.outbox_worker import outbox_worker
from app.presentation.api.dependencies import build_process_outbox_use_case_for_lifespan, build_process_shipping_event_use_case_for_lifespan
from app.config.setting import settings

@asynccontextmanager
async def lifespan(app: FastAPI):

    publisher = KafkaEventPublisher(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    await publisher.start()

    outbox_use_case = build_process_outbox_use_case_for_lifespan(publisher)
    outbox_task = asyncio.create_task(outbox_worker(outbox_use_case(topic=settings.KAFKA_ORDER_TOPIC)))

    consumer = KafkaEventConsumer(topic=settings.KAFKA_SHIPMENT_TOPIC,
                                  bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                                  group_id="order-service")

    await consumer.start()

    inbox_use_case = build_process_shipping_event_use_case_for_lifespan()
    inbox_task = asyncio.create_task(consumer.consume(inbox_use_case))

    try:
        yield
    finally:
        outbox_task.cancel()
        inbox_task.cancel()

        for task in (outbox_task, inbox_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

        await consumer.stop()
        await publisher.stop()