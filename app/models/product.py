from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    # Every item needs a unique ID in the database
    id = Column(Integer, primary_key=True, index=True)
    
    # The actual details of the auto part
    sku = Column(String, unique=True, index=True, nullable=False) # e.g., SP-001
    name = Column(String, index=True, nullable=False)             # e.g., NGK Spark Plug
    category = Column(String, index=True)                         # e.g., Electrical
    image_url = Column(String, nullable=True)                     # Product preview image URL
    stock_quantity = Column(Integer, default=0)                   # e.g., 45
    price = Column(Float, nullable=False)                         # e.g., 350.00