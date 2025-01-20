from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, Enum
from sqlalchemy.orm import relationship
from app.models.Mysql.Base import Base
from app.models.Mysql.Eunums import StoreStatus

class StoreDetails(Base):
    __tablename__ = 'store_details'
    
    """
    SQLAlchemy model for the StoreDetails table.
    """

    store_id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(255), doc="store name for the store")
    license_number = Column(String(50), doc="license number for the store")
    gst_state_code = Column(String(10), doc="GST State Code for the store")
    gst_number = Column(String(50), doc="GST Number for the store")
    pan = Column(String(10), doc="PAN Number for the store")
    address = Column(Text, doc="Address of the store")
    email = Column(String(100), doc="Email Address for the store")
    mobile = Column(String(15), doc="Modile number for the store")
    owner_name = Column(String(255), doc="Owner name of the store")
    is_main_store = Column(Boolean, doc="Is Main of the stores")
    latitude = Column(DECIMAL(10, 6), doc="Latitude of the store")
    longitude = Column(DECIMAL(10, 6), doc="Longitude of the store")
    status = Column(Enum(StoreStatus), doc="Status of the store Active, InActive, Closed")
    users = relationship('User', back_populates='store')