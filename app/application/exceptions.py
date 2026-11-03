from uuid import UUID

class ItemOutOfStockError(Exception):
    def __init__(self):
        self.detail = "Item is out of stock"

        super().__init__(self.detail)

class InsufficientQuantityError(Exception):
    def __init__(self):
        self.detail = "Insufficient quantity"

        super().__init__(self.detail)

class OrderNotFoundException(Exception):
    def __init__(self, order_id: UUID):
        self.detail = f"Order {order_id} is not found"

        super().__init__(self.detail)

class PaymentCreationException(Exception):
    def __init__(self):
        self.detail = "Payment failed"

        super().__init__(self.detail)

class PaymentCreationUnknownException(Exception):
    def __init__(self):
        self.detail = "Payment result is unknown"

        super().__init__(self.detail)

class PaymentAmountMismatchException(Exception):
    def __init__(self):
        self.detail = "Invalid payment amount"

        super().__init__(self.detail)

class PaymentMismatchException(Exception):
    def __init__(self):
        self.detail = "Invalid payment id"

        super().__init__(self.detail)

class PaymentStatusConflictException(Exception):
     def __init__(self):
        self.detail = "Received payment status conflicts with the previously saved status"

        super().__init__(self.detail)

class InvalidPaymentStatusException (Exception):
    def __init__(self):
        self.detail = "Invalid payment status"

        super().__init__(self.detail)

class InvalidEventTypeException(Exception):
    def __init__(self, event_type):
        self.detail = f"Invalid event type: {event_type}"

        super().__init__(self.detail)

class InvalidEventPayloadException(Exception):
    def __init__(self):
        self.detail = "Invalid order_id in shipping event"
