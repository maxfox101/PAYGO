from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class DocumentType(str, enum.Enum):
    """Типы правовых документов"""
    OFFER = "offer"  # Публичная оферта
    TERMS = "terms"  # Условия использования
    PRIVACY = "privacy"  # Политика конфиденциальности
    AGREEMENT = "agreement"  # Пользовательское соглашение

class LegalDocument(Base):
    """Модель правового документа"""
    __tablename__ = "legal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(DocumentType), nullable=False, index=True)
    version = Column(String(20), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    requires_acceptance = Column(Boolean, default=True)
    effective_date = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    class Config:
        orm_mode = True

class UserDocumentAcceptance(Base):
    """Модель принятия документов пользователем"""
    __tablename__ = "user_document_acceptances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    accepted_at = Column(DateTime, default=func.now())
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    
    class Config:
        orm_mode = True
