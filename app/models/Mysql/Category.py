from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.mysql import Base

class Category(Base):
    __tablename__ = 'category'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255))
    medicines = relationship("MedicineMaster", back_populates="category")