from enum import StrEnum

class OrderStatus(StrEnum):
    NEW = 'new'
    PAID = 'paid'
    SHIPPED = 'shipped'
    CANCELLED = 'cancelled'
