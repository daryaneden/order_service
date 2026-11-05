from httpx import AsyncClient, TimeoutException, HTTPStatusError, RequestError
import logging

from app.application.ports.notification_port import NotificationPort
from app.application.dtos.notification_message import NotificationMessage

logger = logging.getLogger(__name__)

class NotificationClient(NotificationPort):

    def __init__(self, client: AsyncClient):

        self.client = client

    async def send_notification(self, notification: NotificationMessage) -> None:
        try:
            response = await self.client.post(f"/api/notifications",
                                              json={"message": notification.message,
                                                    "reference_id": notification.reference_id,
                                                    "idempotency_key": notification.idempotency_key})

            response.raise_for_status()

        except TimeoutException:
            logger.warning(
                "Notification request for order %s timed out",
                notification.reference_id,
            )

        except HTTPStatusError as exc:
            logger.warning(
                "Notifications Service returned status %s for order %s",
                exc.response.status_code,
                notification.reference_id,
            )

        except RequestError:
            logger.exception(
                "Could not send notification for order %s",
                notification.reference_id,
            )