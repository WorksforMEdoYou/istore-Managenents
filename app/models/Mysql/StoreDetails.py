from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, Enum
from sqlalchemy.orm import relationship
from app.db.mysql import Base
from app.schemas.mysql_schema import StoreStatus

class StoreDetails(Base):
    __tablename__ = 'store_details'
    
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(255))
    license_number = Column(String(50))
    gst_state_code = Column(String(10))
    gst_number = Column(String(50))
    pan = Column(String(10))
    address = Column(Text)
    email = Column(String(100))
    mobile = Column(String(15))
    owner_name = Column(String(255))
    is_main_store = Column(Boolean)
    latitude = Column(DECIMAL(10, 6))
    longitude = Column(DECIMAL(10, 6))
    status = Column(Enum(StoreStatus))
    users = relationship('User', back_populates='store')