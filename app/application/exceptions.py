from uuid import UUID

class ItemOutOfStockError(Exception):
    def __init__(self):
            self.detail = "Item is out of stock"

class InsufficientQuantityError(Exception):
    def __init__(self):
            self.detail = "Insufficient quantity"

class OrderNotFoundException(Exception):
    def __init__(self, order_id: UUID):
        self.detail = f"Order {order_id} is not found"

class PaymentCreationException(Exception):
    def __init__(self):
        self.detail = "Payment failed"

class PaymentCreationUnknownException(Exception):
    def __init__(self):
        self.detail = "Payment result is unknown"

class PaymentAmountMismatchException(Exception):
    def __init__(self):
        self.detail = "Invalid payment amount"

class PaymentMismatchException(Exception):
    def __init__(self):
        self.detail = "Invalid payment id"

class PaymentStatusConflictException(Exception):
     def __init__(self):
             self.detail = "Received payment status conflicts with the previously saved status."

class InvalidPaymentStatusException (Exception):
     def __init__(self):
             self.detail = "Invalid payment status"