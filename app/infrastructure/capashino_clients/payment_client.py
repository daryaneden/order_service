from httpx import AsyncClient, TimeoutException, ConnectError, HTTPStatusError, RequestError
from uuid import UUID
from decimal import Decimal

from app.application.ports.payment_port import PaymentPort
from app.application.dtos.payment_dtos import CreatePaymentDto, PaymentDto
from app.domain.enums.payment_status import PaymentStatus
from app.application.exceptions import PaymentCreationException, PaymentCreationUnknownException

class PaymentClient(PaymentPort):

    def __init__(self, client: AsyncClient):
        self.client = client

    async def create_payment(self, data: CreatePaymentDto) -> PaymentDto:
        try:
            response = await self.client.post(
                "/api/payments",
                json={
                    "order_id": str(data.order_id),
                    "amount": str(data.amount),
                    "callback_url": data.callback_url,
                    "idempotency_key": data.idempotency_key,
                },
            )

            response.raise_for_status()
            payload = response.json()

            return PaymentDto(
                id=UUID(payload["id"]),
                order_id=UUID(payload["order_id"]),
                amount=Decimal(payload["amount"]),
                status=PaymentStatus(payload["status"]),
                idempotency_key=payload["idempotency_key"],
            )

        except TimeoutException as exc:
            raise PaymentCreationUnknownException() from exc

        except ConnectError as exc:
            raise PaymentCreationUnknownException() from exc

        except HTTPStatusError as exc:
            if exc.response.status_code in (400, 401, 403, 404, 422):
                raise PaymentCreationException() from exc

            raise PaymentCreationUnknownException() from exc

        except RequestError as exc:
            raise PaymentCreationUnknownException() from exc

