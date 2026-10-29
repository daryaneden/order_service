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