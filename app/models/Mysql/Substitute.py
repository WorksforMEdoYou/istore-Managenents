from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.mysql import Base

class Substitutes(Base):
    __tablename__ = 'substitutes'
    
    substitute_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicine_master.medicine_id'))
    substitute_medicine = Column(String(255))