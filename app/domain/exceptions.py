from app.domain.enums.order_status import OrderStatus


class InvalidOrderQuantityError(Exception):
    def __init__(self):
        self.detail = "Order quantity is not positive"

        super().__init__(self.detail)


class InvalidOrderPriceError(Exception):
    def __init__(self):
        self.detail = "Order price can not be negative"

        super().__init__(self.detail)


class InvalidOrderStatusTransitionError(Exception):
    def __init__(self, current_status: OrderStatus, new_status: OrderStatus):
        self.detail = (
            f"Cannot change order status from {current_status} to {new_status}"
        )

        super().__init__(self.detail)
