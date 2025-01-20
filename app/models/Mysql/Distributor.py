from sqlalchemy import Column, Integer, String
from app.models.Mysql.Base import Base

class Distributor(Base):
    __tablename__ = 'distributor'
    
    """
    SQLAlchemy model for the distributor table.
    """
    
    distributor_id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_name = Column(String(255), doc="disttributor name for medicine_master")