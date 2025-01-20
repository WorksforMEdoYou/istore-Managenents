from enum import Enum

class StoreStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

class UserRole(str, Enum):
    SHOP_KEEPER = "store_keeper" 
    ADMIN = "admin" 
    CONSUMER = "consumer"
