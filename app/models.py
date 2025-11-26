from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)  # максимальное количество активных обращений
    current_load = Column(Integer, default=0)  # текущее количество активных обращений
    
    # Связь с весами по источникам
    source_weights = relationship("OperatorSourceWeight", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # уникальный идентификатор лида
    email = Column(String, index=True)
    phone = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    contacts = relationship("Contact", back_populates="lead")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    operator_weights = relationship("OperatorSourceWeight", back_populates="source")
    contacts = relationship("Contact", back_populates="source")

class OperatorSourceWeight(Base):
    __tablename__ = "operator_source_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Integer, default=1)  # вес оператора для данного источника
    
    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    message = Column(String)
    status = Column(String, default="new")  # new, in_progress, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
