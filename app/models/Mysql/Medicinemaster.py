from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.mysql import Base

class MedicineMaster(Base):
    __tablename__ = 'medicine_master'
    
    medicine_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(255))
    generic_name = Column(String(255))
    hsn_code = Column(String(10))
    formulation = Column(String(50))
    strength = Column(String(50))
    unit_of_measure = Column(String(10))
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.manufacturer_id'))
    category_id = Column(Integer, ForeignKey('category.category_id'))
    manufacturer = relationship("Manufacturer", back_populates="medicines")
    category = relationship("Category", back_populates="medicines")