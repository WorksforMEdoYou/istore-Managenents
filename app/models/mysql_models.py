from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..db.mysql import Base

class StoreDetails(Base):
    __tablename__ = 'store_details'
    
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(255))
    license_number = Column(String(50))
    gst_state_code = Column(String(2))
    gst_number = Column(String(15))
    pan = Column(String(10))
    address = Column(Text)
    email = Column(String(255))
    mobile = Column(String(15))
    owner_name = Column(String(255))
    is_main_store = Column(Boolean)
    latitude = Column(DECIMAL(10, 6))
    longitude = Column(DECIMAL(10, 6))
    status = Column(String(255))

class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    
    manufacturer_id = Column(Integer, primary_key=True, autoincrement=True)
    manufacturer_name = Column(String(255))

class Category(Base):
    __tablename__ = 'category'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255))

class MedicineMaster(Base):
    __tablename__ = 'medicine_master'
    
    medicine_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(255))
    generic_name = Column(String(255))
    hsn_code = Column(String(10))
    formulation = Column(String(50))
    strength = Column(String(50))
    batch = Column(String(50))
    unit_of_measure = Column(String(10))
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.manufacturer_id'))
    category_id = Column(Integer, ForeignKey('category.category_id'))

class Substitutes(Base):
    __tablename__ = 'substitutes'
    
    substitute_id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicine_master.medicine_id'))
    substitute_medicine = Column(String(255))

class Distributor(Base):
    __tablename__ = 'distributor'
    
    distributor_id = Column(Integer, primary_key=True, autoincrement=True)
    distributor_name = Column(String(255))

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password_hash = Column(String(255))
    role = Column(Enum('store_keeper', 'admin', 'consumer'))
    store_id = Column(Integer, ForeignKey('store_details.store_id'))