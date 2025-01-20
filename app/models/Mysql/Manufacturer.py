from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.Mysql.Base import Base

class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    
    """
    SQLAlchemy model for the manufacturer table.
    """

    manufacturer_id = Column(Integer, primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255), doc="manufacturer_name for the medicine_master")
    medicines = relationship("MedicineMaster", back_populates="manufacturer")