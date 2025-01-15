from sqlalchemy import Column, Integer, String
from app.db.mysql import Base

class Distributor(Base):
    __tablename__ = 'distributor'
    
    distributor_id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_name = Column(String(255))