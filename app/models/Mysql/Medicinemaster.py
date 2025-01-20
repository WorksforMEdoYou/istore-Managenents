from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.Mysql.Base import Base

class MedicineMaster(Base):
    __tablename__ = 'medicine_master'
    
    """
    SQLAlchemy model for the medicine_master table.
    """
    
    medicine_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(255), doc="Name of the medicine")
    generic_name = Column(String(255), doc="Generic name of the medicine")
    hsn_code = Column(String(10), doc="HSN code of the medicine")
    formulation = Column(String(50), doc="Formula of the medicine")
    strength = Column(String(50), doc="Stength of the medicine")
    unit_of_measure = Column(String(10), doc="Unit of Measure of the medicine")
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.manufacturer_id'), doc="ID of the Manufacturer")
    category_id = Column(Integer, ForeignKey('category.category_id'), doc="ID of the Category")
    manufacturer = relationship("Manufacturer", back_populates="medicines")
    category = relationship("Category", back_populates="medicines")