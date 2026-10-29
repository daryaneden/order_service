class ItemOutOfStockError(Exception):
    def __init__(self):
            self.detail = "Item is out of stock"

class InsufficientQuantityError(Exception):
    def __init__(self):
            self.detail = "Insufficient quantity"

class OrderNotFoundException(Exception):
    def __init__(self):
        self.detail = "Order is not found"