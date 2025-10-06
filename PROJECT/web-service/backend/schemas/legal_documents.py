from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """Типы правовых документов"""
    OFFER = "offer"
    TERMS = "terms"
    PRIVACY = "privacy"
    AGREEMENT = "agreement"

class LegalDocumentBase(BaseModel):
    """Базовая схема правового документа"""
    type: DocumentType
    version: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    requires_acceptance: bool = True
    
    @validator('version')
    def validate_version(cls, v):
        """Валидация версии документа"""
        if not v.replace('.', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Версия должна содержать только буквы, цифры, точки, дефисы и подчеркивания')
        return v

class LegalDocumentCreate(LegalDocumentBase):
    """Схема для создания документа"""
    pass

class LegalDocumentUpdate(BaseModel):
    """Схема для обновления документа"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    requires_acceptance: Optional[bool] = None
    is_active: Optional[bool] = None

class LegalDocumentResponse(LegalDocumentBase):
    """Схема для ответа с документом"""
    id: int
    is_active: bool
    effective_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class DocumentAcceptanceRequest(BaseModel):
    """Схема для принятия документа"""
    document_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class DocumentAcceptanceResponse(BaseModel):
    """Схема для ответа о принятии документа"""
    id: int
    user_id: int
    document_id: int
    accepted_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    class Config:
        orm_mode = True

class UserDocumentsStatus(BaseModel):
    """Статус документов пользователя"""
    user_id: int
    documents: List[dict] = []
    pending_acceptance: List[int] = []
    
    class Config:
        orm_mode = True

class DocumentVersionHistory(BaseModel):
    """История версий документа"""
    document_id: int
    versions: List[dict] = []
    
    class Config:
        orm_mode = True
