from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.Mysql.Base import Base

class Category(Base):
    __tablename__ = 'category'
    
    """
    SQLAlchemy model for the category table.
    """
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), doc="category name of the medicine")
    medicines = relationship("MedicineMaster", back_populates="category")