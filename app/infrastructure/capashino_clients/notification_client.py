from httpx import AsyncClient, TimeoutException, HTTPStatusError, RequestError
import logging

from app.application.ports.notification_port import NotificationPort
from app.application.dtos.notification_message import NotificationMessage

logger = logging.getLogger(__name__)

class NotificationClient(NotificationPort):

    def __init__(self, client: AsyncClient):

        self.client = client

    async def send_notification(self, notification: NotificationMessage) -> None:
        logger.info(
        "Sending notification: reference_id=%s, idempotency_key=%s, message=%s",
        notification.reference_id,
        notification.idempotency_key,
        notification.message,
    )
        try:
            response = await self.client.post(f"/api/notifications",
                                              json={"message": notification.message,
                                                    "reference_id": str(notification.reference_id),
                                                    "idempotency_key": notification.idempotency_key})
            logger.info(
                "Notification sent successfully: reference_id=%s, status_code=%s",
                notification.reference_id,
                response.status_code)
            
            response.raise_for_status()

            logger.info(
    "Notification sent successfully: order_id=%s, idempotency_key=%s, status=%s",
    notification.reference_id,
    notification.idempotency_key,
    response.status_code,
)

        except TimeoutException:
            logger.warning(
                "Notification request for order %s timed out",
                notification.reference_id,
            )

        except HTTPStatusError as exc:
            logger.warning(
        "Notifications Service returned an error for order %s. "
        "Status: %s. Response: %s",
        notification.reference_id,
        exc.response.status_code,
        exc.response.text,
    )

        except RequestError:
            logger.exception(
                "Could not send notification for order %s",
                notification.reference_id,
            )