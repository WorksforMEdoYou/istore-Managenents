from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.mysql import Base
from app.schemas.mysql_schema import UserRole

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password_hash = Column(String(255))
    role = Column(Enum(UserRole))
    store_id = Column(Integer, ForeignKey('store_details.store_id'))
    store = relationship('StoreDetails', back_populates='users')