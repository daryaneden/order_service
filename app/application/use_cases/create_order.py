from uuid import UUID, uuid4

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.dtos.order import OrderDto
from app.application.dtos.payment_dtos import CreatePaymentDto
from app.application.dtos.outbox_message import OutboxMessageDto, EventType
from app.application.ports.catalog_port import CatalogPort
from app.application.ports.payment_port import PaymentPort
from app.application.exceptions import InsufficientQuantityError, ItemOutOfStockError, PaymentCreationException, PaymentCreationUnknownException, PaymentMismatchException, PaymentAmountMismatchException, InvalidPaymentStatusException, PaymentStatusConflictException, OrderNotFoundException
from app.domain.entities.order import Order
from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus

import logging

logger = logging.getLogger(__name__)

# class CreateOrderUseCase():

#     def __init__(self, uow_factory: UnitOfWorkFactory,
#         catalog_port: CatalogPort,
#         payment_port: PaymentPort,
#         callback_url: str):
        
#         self.uow_factory = uow_factory
#         self.catalog_port = catalog_port
#         self.payment_port = payment_port
#         self.callback_url = callback_url

#     async def __call__(self, order_data: OrderDto):
#         async with self.uow_factory() as uow:
#             existing_order = await uow.order_repository.get_by_idempotency_key(
#                 order_data.idempotency_key
#             )

#         if existing_order is not None:
#             if existing_order.status in (OrderStatus.PAID,
#                                          OrderStatus.CANCELLED):
#                 return existing_order
            
#             if existing_order.payment_id is not None:
#                 return existing_order

#             return await self._create_payment(existing_order)

#         item = await self.catalog_port.get_item(order_data.item_id)

#         if item.available_qty <= 0:
#             raise ItemOutOfStockError()

#         if item.available_qty < order_data.quantity:
#             raise InsufficientQuantityError()

#         order = Order(
#             id=uuid4(),
#             user_id=order_data.user_id,
#             item_id=order_data.item_id,
#             quantity=order_data.quantity,
#             unit_price=item.price,
#             status=OrderStatus.NEW,
#             idempotency_key=order_data.idempotency_key)

#         async with self.uow_factory() as uow:
#             await uow.order_repository.create_order(order)

#         return await self._create_payment(order)

#     async def _create_payment(self, order: Order) -> Order:
#         payment_data = CreatePaymentDto(
#             order_id=order.id,
#             amount=order.unit_price * order.quantity,
#             callback_url=self.callback_url,
#             idempotency_key=order.idempotency_key,
#         )

#         logger.info(
#             "Sending payment creation request: order_id=%s",
#             order.id,
#         )

#         try:
#             payment = await self.payment_port.create_payment(payment_data)

#             logger.info(
#             "Payment creation response received: order_id=%s, "
#             "payment_id=%s, payment_status=%s",
#             order.id,
#             payment.id,
#             payment.status,
#         )

#         except PaymentCreationUnknownException:
#             raise

#         except PaymentCreationException:
#             async with self.uow_factory() as uow:
#                 order.status = OrderStatus.CANCELLED
#                 await uow.order_repository.update_order(order)

#             raise

#         async with self.uow_factory() as uow:
#             order = await uow.order_repository.get_order_by_id_for_update(order.id)
#             if order is None:
#                 raise OrderNotFoundException()
            
#             order.payment_id = payment.id
#             order.payment_status = payment.status

#             pending_callbacks = (await uow.pending_payment_callback_repository.get_all_by_order_id(order.id))
#              # 4. Обрабатываем каждый отложенный callback.
#             for callback in pending_callbacks:
#                 if callback.payment_id != order.payment_id:
#                     raise PaymentMismatchException()

#                 expected_amount = order.unit_price * order.quantity

#                 if callback.amount != expected_amount:
#                     raise PaymentAmountMismatchException()

#                 # Повторный callback с тем же уже применённым
#                 # терминальным статусом не должен создавать событие повторно.
#                 if (
#                     order.payment_status == PaymentStatus.SUCCEEDED
#                     and order.status == OrderStatus.PAID
#                     and callback.status == PaymentStatus.SUCCEEDED
#                 ):
#                     await uow.pending_payment_callback_repository.delete(
#                         callback.id
#                     )
#                     continue

#                 if (
#                     order.payment_status == PaymentStatus.FAILED
#                     and order.status == OrderStatus.CANCELLED
#                     and callback.status == PaymentStatus.FAILED
#                 ):
#                     await uow.pending_payment_callback_repository.delete(
#                         callback.id
#                     )
#                     continue

#                 # Если платёж уже завершился другим терминальным статусом,
#             # противоречащий callback обрабатывать нельзя.
#                 if order.payment_status in (
#                     PaymentStatus.SUCCEEDED,
#                     PaymentStatus.FAILED,
#                 ):
#                     raise PaymentStatusConflictException()

#                 if order.payment_status != PaymentStatus.PENDING:
#                     raise PaymentStatusConflictException()

#                 if callback.status == PaymentStatus.SUCCEEDED:
#                     order.payment_status = PaymentStatus.SUCCEEDED
#                     order.status = OrderStatus.PAID

#                     event = OutboxMessageDto(
#                         event_type=EventType.ORDER_PAID,
#                         payload={
#                             "event_type": EventType.ORDER_PAID.value,
#                             "order_id": str(order.id),
#                             "item_id": str(order.item_id),
#                             "quantity": int(order.quantity),
#                             "idempotency_key": str(order.idempotency_key),
#                         },
#                     )

#                 elif callback.status == PaymentStatus.FAILED:
#                     order.payment_status = PaymentStatus.FAILED
#                     order.status = OrderStatus.CANCELLED

#                 else:
#                     raise InvalidPaymentStatusException()

#                 await uow.pending_payment_callback_repository.delete(
#                 callback.id
#             )


#                 await uow.outbox_repository.save(event)

#             await uow.order_repository.update_order(order)

#         return order


logger = logging.getLogger(__name__)


class CreateOrderUseCase:

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        catalog_port: CatalogPort,
        payment_port: PaymentPort,
        callback_url: str,
    ):
        self.uow_factory = uow_factory
        self.catalog_port = catalog_port
        self.payment_port = payment_port
        self.callback_url = callback_url

    async def __call__(self, order_data: OrderDto) -> Order:

        # 1. Проверяем, существует ли заказ с таким idempotency_key.
        async with self.uow_factory() as uow:
            existing_order = (
                await uow.order_repository.get_by_idempotency_key(
                    order_data.idempotency_key
                )
            )

        if existing_order is not None:

            if existing_order.status in (
                OrderStatus.PAID,
                OrderStatus.CANCELLED,
            ):
                return existing_order

            # Платёж уже создан. Повторно обращаться к Payment Service
            # не нужно.
            if existing_order.payment_id is not None:
                return existing_order

            # Если предыдущая попытка создания платежа завершилась
            # неопределённым результатом, повторяем запрос с тем же
            # idempotency_key.
            return await self._create_payment(existing_order)

        # 2. Получаем информацию о товаре из Catalog Service.
        item = await self.catalog_port.get_item(order_data.item_id)

        if item.available_qty <= 0:
            raise ItemOutOfStockError()

        if item.available_qty < order_data.quantity:
            raise InsufficientQuantityError()

        # 3. Создаём заказ.
        order = Order(
            id=uuid4(),
            user_id=order_data.user_id,
            item_id=order_data.item_id,
            quantity=order_data.quantity,
            unit_price=item.price,
            status=OrderStatus.NEW,
            idempotency_key=order_data.idempotency_key,
        )

        # 4. Сохраняем заказ до обращения к Payment Service.
        async with self.uow_factory() as uow:
            await uow.order_repository.create_order(order)

        # 5. Создаём платёж.
        return await self._create_payment(order)

    async def _create_payment(self, order: Order) -> Order:

        payment_data = CreatePaymentDto(
            order_id=order.id,
            amount=order.unit_price * order.quantity,
            callback_url=self.callback_url,
            idempotency_key=order.idempotency_key,
        )

        logger.info(
            "Sending payment creation request: order_id=%s",
            order.id,
        )

        try:
            # Внешний HTTP-запрос выполняется вне транзакции БД.
            payment = await self.payment_port.create_payment(payment_data)

            logger.info(
                "Payment creation response received: order_id=%s, "
                "payment_id=%s, payment_status=%s",
                order.id,
                payment.id,
                payment.status,
            )

        except PaymentCreationUnknownException:
            # Неизвестно, создал ли Payment Service платёж.
            # Не отменяем заказ: при повторном запросе используем
            # тот же idempotency_key.
            raise

        except PaymentCreationException:
            # Если Payment Service определённо сообщил об ошибке
            # создания платежа, отменяем заказ.
            async with self.uow_factory() as uow:

                locked_order = (
                    await uow.order_repository.get_order_by_id_for_update(
                        order.id
                    )
                )

                if locked_order is None:
                    raise OrderNotFoundException()

                locked_order.status = OrderStatus.CANCELLED

                await uow.order_repository.update_order(locked_order)

            raise

        # 6. Сохраняем результат Payment Service и обрабатываем
        # отложенные callback в одной транзакции.
        async with self.uow_factory() as uow:

            locked_order = (
                await uow.order_repository.get_order_by_id_for_update(
                    order.id
                )
            )

            if locked_order is None:
                raise OrderNotFoundException()

            # Сохраняем идентификатор платежа.
            locked_order.payment_id = payment.id

            # Применяем статус, который вернул Payment Service.
            await self._apply_payment_status(
                uow=uow,
                order=locked_order,
                payment_status=payment.status,
            )

            # 7. Получаем callback, которые пришли до сохранения
            # payment_id.
            pending_callbacks = (
                await uow.pending_payment_callback_repository
                .get_all_by_order_id(locked_order.id)
            )

            for callback in pending_callbacks:

                # Проверяем, что callback относится к нашему платежу.
                if callback.payment_id != locked_order.payment_id:
                    raise PaymentMismatchException()

                # Проверяем сумму платежа.
                expected_amount = (
                    locked_order.unit_price * locked_order.quantity
                )

                if callback.amount != expected_amount:
                    raise PaymentAmountMismatchException()

                # Применяем статус callback.
                # Если он совпадает с уже применённым терминальным
                # статусом, событие повторно не создаётся.
                await self._apply_payment_status(
                    uow=uow,
                    order=locked_order,
                    payment_status=callback.status,
                )

                # Удаляем обработанный callback.
                await uow.pending_payment_callback_repository.delete(
                    callback.id
                )

            # 8. Сохраняем заказ.
            # Outbox-событие, если оно было создано, будет закоммичено
            # в той же транзакции.
            await uow.order_repository.update_order(locked_order)

        return locked_order

    async def _apply_payment_status(
        self,
        order: Order,
        payment_status: PaymentStatus,
    ) -> None:

        # Если статус уже терминальный, повторное применение
        # того же результата не должно создавать новое событие.
        if order.payment_status in (
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
        ):

            if order.payment_status == payment_status:
                return

            raise PaymentStatusConflictException()

        # PENDING означает, что платёж ещё не завершён.
        if payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.PENDING
            order.status = OrderStatus.NEW
            return

        # Успешная оплата.
        if payment_status == PaymentStatus.SUCCEEDED:

            order.payment_status = PaymentStatus.SUCCEEDED
            order.status = OrderStatus.PAID

            # Создаём событие для Shipment Service.
            event = OutboxMessageDto(
                event_type=EventType.ORDER_PAID,
                payload={
                    "event_type": EventType.ORDER_PAID.value,
                    "order_id": str(order.id),
                    "item_id": str(order.item_id),
                    "quantity": int(order.quantity),
                    "idempotency_key": str(order.idempotency_key),
                },
            )

            async with self.uow_factory() as uow:
            

                await uow.outbox_repository.save(event)

            logger.info(
                "ORDER_PAID event added to outbox: order_id=%s",
                order.id,
            )

            return

        # Неуспешная оплата.
        if payment_status == PaymentStatus.FAILED:

            order.payment_status = PaymentStatus.FAILED
            order.status = OrderStatus.CANCELLED

            logger.info(
                "Payment failed: order_id=%s",
                order.id,
            )

            return

        raise InvalidPaymentStatusException()