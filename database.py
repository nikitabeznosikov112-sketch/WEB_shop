from sqlalchemy import Column, Integer, ForeignKey, String, create_engine, Boolean, DateTime, func, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()
Session = sessionmaker(bind=engine)
        
class Seller(Base):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String(120), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)

    deals = relationship('Deal', back_populates='seller')
    products = relationship('Product', back_populates='seller')
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    date = Column(DateTime(timezone=True), default = func.now(), nullable=False)
    favorites = Column(Integer, nullable=True, default=0)

    seller = relationship('Seller', back_populates='products')
    deal = relationship('Deal', back_populates='product')

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String(120), nullable=False)
    password_hash = Column(Text, nullable=False)

    deal = relationship('Deal', back_populates="client")

class Deal(Base):
    __tablename__ = 'deals'

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    status = Column(Boolean, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    active = Column(Boolean, nullable=False, default=True)

    seller = relationship('Seller', back_populates='deals')
    product = relationship('Product', back_populates='deal')
    client = relationship('Client', back_populates='deal')
