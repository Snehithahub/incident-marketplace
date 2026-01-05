# models.py
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)  # e.g., farmer, plumber, caretaker
    phone = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
