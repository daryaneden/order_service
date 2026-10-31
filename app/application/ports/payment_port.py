from abc import ABC, abstractmethod

from app.application.dtos.payment_dtos import CreatePaymentDto, PaymentDto


class PaymentPort(ABC):

    @abstractmethod
    async def create_payment(self, data: CreatePaymentDto) -> PaymentDto:
        pass