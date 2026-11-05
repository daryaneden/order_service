import asyncio
import logging

from app.application.use_cases.process_outbox import ProcessOutboxUseCase

logger = logging.getLogger(__name__)

async def outbox_worker(use_case: ProcessOutboxUseCase, topic: str) -> None:
    while True:
        try:
            logger.info('Starting outbox processing')

            await use_case(topic)

            logger.info('Outbox processing completed')

        except Exception:
            logger.exception('Outbox processing failed')

        await asyncio.sleep(60)
