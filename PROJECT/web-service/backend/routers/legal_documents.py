from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import get_db
from services.legal_documents_service import LegalDocumentsService
from schemas.legal_documents import (
    LegalDocumentCreate, LegalDocumentUpdate, LegalDocumentResponse,
    DocumentAcceptanceRequest, DocumentAcceptanceResponse,
    UserDocumentsStatus, DocumentVersionHistory
)
from models.legal_documents import DocumentType
from auth.dependencies import get_current_user, get_current_admin_user
from models.user import User
from models.user_document_acceptance import UserDocumentAcceptance

router = APIRouter(prefix="/api/legal", tags=["Правовые документы"])
logger = logging.getLogger(__name__)

@router.get("/documents/{document_type}", response_model=LegalDocumentResponse)
async def get_active_document(
    document_type: DocumentType,
    db: Session = Depends(get_db)
):
    """Получение активного документа по типу"""
    service = LegalDocumentsService(db)
    document = service.get_active_document(document_type)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Активный документ типа {document_type.value} не найден"
        )
    
    return document

@router.get("/documents/{document_type}/history", response_model=List[dict])
async def get_document_history(
    document_type: DocumentType,
    db: Session = Depends(get_db)
):
    """Получение истории версий документа"""
    service = LegalDocumentsService(db)
    return service.get_document_version_history(document_type)

@router.get("/documents/{document_type}/versions", response_model=List[LegalDocumentResponse])
async def get_document_versions(
    document_type: DocumentType,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Получение всех версий документа по типу"""
    service = LegalDocumentsService(db)
    return service.get_documents_by_type(document_type, include_inactive)

@router.get("/user/status", response_model=UserDocumentsStatus)
async def get_user_documents_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статуса документов текущего пользователя"""
    service = LegalDocumentsService(db)
    return service.get_user_documents_status(current_user.id)

@router.post("/user/accept", response_model=DocumentAcceptanceResponse)
async def accept_document(
    acceptance_data: DocumentAcceptanceRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Принятие документа пользователем"""
    service = LegalDocumentsService(db)
    
    # Получаем IP адрес и User-Agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    success = service.accept_document(
        user_id=current_user.id,
        document_id=acceptance_data.document_id,
        ip_address=ip_address or acceptance_data.ip_address,
        user_agent=user_agent or acceptance_data.user_agent
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось принять документ. Возможно, документ не существует или неактивен."
        )
    
    # Получаем информацию о принятии
    acceptance = db.query(UserDocumentAcceptance).filter(
        UserDocumentAcceptance.user_id == current_user.id,
        UserDocumentAcceptance.document_id == acceptance_data.document_id
    ).first()
    
    return acceptance

@router.get("/user/acceptances", response_model=List[DocumentAcceptanceResponse])
async def get_user_acceptances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех принятых пользователем документов"""
    acceptances = db.query(UserDocumentAcceptance).filter(
        UserDocumentAcceptance.user_id == current_user.id
    ).all()
    
    return acceptances

# Административные endpoints
@router.post("/admin/documents", response_model=LegalDocumentResponse)
async def create_document(
    document_data: LegalDocumentCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создание нового правового документа (только для администраторов)"""
    service = LegalDocumentsService(db)
    return service.create_document(document_data)

@router.put("/admin/documents/{document_id}", response_model=LegalDocumentResponse)
async def update_document(
    document_id: int,
    update_data: LegalDocumentUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновление правового документа (только для администраторов)"""
    service = LegalDocumentsService(db)
    document = service.update_document(document_id, update_data)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    return document

@router.delete("/admin/documents/{document_id}")
async def deactivate_document(
    document_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Деактивация правового документа (только для администраторов)"""
    service = LegalDocumentsService(db)
    success = service.deactivate_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    return {"message": "Документ успешно деактивирован"}

@router.get("/admin/documents/{document_id}/stats")
async def get_document_stats(
    document_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение статистики принятия документа (только для администраторов)"""
    service = LegalDocumentsService(db)
    return service.get_document_acceptance_stats(document_id)

@router.get("/admin/documents", response_model=List[LegalDocumentResponse])
async def get_all_documents(
    include_inactive: bool = False,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение всех документов (только для администраторов)"""
    service = LegalDocumentsService(db)
    documents = []
    
    for doc_type in DocumentType:
        docs = service.get_documents_by_type(doc_type, include_inactive)
        documents.extend(docs)
    
    return documents

# Публичные endpoints для отображения документов
@router.get("/public/offer")
async def get_public_offer(db: Session = Depends(get_db)):
    """Публичный доступ к оферте"""
    service = LegalDocumentsService(db)
    document = service.get_active_document(DocumentType.OFFER)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Публичная оферта не найдена"
        )
    
    return {
        "id": document.id,
        "type": document.type.value,
        "version": document.version,
        "title": document.title,
        "content": document.content,
        "effective_date": document.effective_date,
        "requires_acceptance": document.requires_acceptance
    }

@router.get("/public/terms")
async def get_public_terms(db: Session = Depends(get_db)):
    """Публичный доступ к условиям использования"""
    service = LegalDocumentsService(db)
    document = service.get_active_document(DocumentType.TERMS)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Условия использования не найдены"
        )
    
    return {
        "id": document.id,
        "type": document.type.value,
        "version": document.version,
        "title": document.title,
        "content": document.content,
        "effective_date": document.effective_date,
        "requires_acceptance": document.requires_acceptance
    }

@router.get("/public/privacy")
async def get_public_privacy(db: Session = Depends(get_db)):
    """Публичный доступ к политике конфиденциальности"""
    service = LegalDocumentsService(db)
    document = service.get_active_document(DocumentType.PRIVACY)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Политика конфиденциальности не найдена"
        )
    
    return {
        "id": document.id,
        "type": document.type.value,
        "version": document.version,
        "title": document.title,
        "content": document.content,
        "effective_date": document.effective_date,
        "requires_acceptance": document.requires_acceptance
    }
