from sqlalchemy import Integer, String, Column
from app.database import Base, engine
from sqlalchemy.orm import mapped_column, relationship 
from sqlalchemy import ForeignKey

# User model
class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    products = relationship("Product", back_populates="user")

# Product model
class Product(Base):
    __tablename__ = 'products'

    id = mapped_column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer, index=True)
    user_id= mapped_column(ForeignKey('users.id'))
    user = relationship("User", back_populates="products")

# Create all tables in the database
Base.metadata.create_all(bind=engine)
