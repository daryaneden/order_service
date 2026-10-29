class DomainError(Exception):
    pass

class InvalidOrderQuantityError(DomainError):
    def __init__(self):
        self.detail = "Order quantity is not positive."


class InvalidOrderPriceError(DomainError):
    def __init__(self):
            self.detail = "Order price can not be negative"