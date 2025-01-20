from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.mysql import Base
from app.models.Mysql.Eunums import UserRole

class User(Base):
    __tablename__ = 'users'
    
    """
    SQLAlchemy model for the user table.
    """
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), doc="Name of the User")
    password_hash = Column(String(255), doc="User password hashed")
    role = Column(Enum(UserRole), doc="role of the User Shop Keeper, Admin, Consumer")
    store_id = Column(Integer, ForeignKey('store_details.store_id'), doc="Store ID from the store_details table")
    store = relationship('StoreDetails', back_populates='users')