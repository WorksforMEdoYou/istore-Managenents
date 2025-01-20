from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.Mysql.Base import Base

class Substitutes(Base):
    __tablename__ = 'substitutes'
    
    """
    SQLAlchemy model for the medicine substitute table.
    """

    substitute_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicine_master.medicine_id'), doc="Medicine ID from the medicine_master table")
    substitute_medicine = Column(String(255), doc="Substitute Medicine Name for the medicine master")