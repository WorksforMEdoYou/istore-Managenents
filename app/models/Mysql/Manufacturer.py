from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base

class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    
    manufacturer_id = Column(Integer, primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255))
    medicines = relationship("MedicineMaster", back_populates="manufacturer")