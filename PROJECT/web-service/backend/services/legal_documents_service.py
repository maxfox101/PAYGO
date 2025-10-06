from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
import logging

from models.legal_documents import LegalDocument, UserDocumentAcceptance, DocumentType
from schemas.legal_documents import LegalDocumentCreate, LegalDocumentUpdate

logger = logging.getLogger(__name__)

class LegalDocumentsService:
    """Сервис для работы с правовыми документами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(self, document_data: LegalDocumentCreate) -> LegalDocument:
        """Создание нового правового документа"""
        try:
            # Деактивируем предыдущие версии того же типа
            if document_data.requires_acceptance:
                self.db.query(LegalDocument).filter(
                    and_(
                        LegalDocument.type == document_data.type,
                        LegalDocument.is_active == True
                    )
                ).update({"is_active": False})
            
            # Создаем новый документ
            db_document = LegalDocument(
                type=document_data.type,
                version=document_data.version,
                title=document_data.title,
                content=document_data.content,
                requires_acceptance=document_data.requires_acceptance,
                effective_date=datetime.utcnow()
            )
            
            self.db.add(db_document)
            self.db.commit()
            self.db.refresh(db_document)
            
            logger.info(f"Создан новый документ: {document_data.type} v{document_data.version}")
            return db_document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания документа: {e}")
            raise
    
    def get_active_document(self, document_type: DocumentType) -> Optional[LegalDocument]:
        """Получение активного документа по типу"""
        return self.db.query(LegalDocument).filter(
            and_(
                LegalDocument.type == document_type,
                LegalDocument.is_active == True
            )
        ).first()
    
    def get_document_by_id(self, document_id: int) -> Optional[LegalDocument]:
        """Получение документа по ID"""
        return self.db.query(LegalDocument).filter(LegalDocument.id == document_id).first()
    
    def get_documents_by_type(self, document_type: DocumentType, include_inactive: bool = False) -> List[LegalDocument]:
        """Получение документов по типу"""
        query = self.db.query(LegalDocument).filter(LegalDocument.type == document_type)
        
        if not include_inactive:
            query = query.filter(LegalDocument.is_active == True)
        
        return query.order_by(desc(LegalDocument.effective_date)).all()
    
    def update_document(self, document_id: int, update_data: LegalDocumentUpdate) -> Optional[LegalDocument]:
        """Обновление документа"""
        try:
            document = self.get_document_by_id(document_id)
            if not document:
                return None
            
            # Обновляем только переданные поля
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(document, field, value)
            
            document.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"Обновлен документ ID {document_id}")
            return document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления документа: {e}")
            raise
    
    def deactivate_document(self, document_id: int) -> bool:
        """Деактивация документа"""
        try:
            document = self.get_document_by_id(document_id)
            if not document:
                return False
            
            document.is_active = False
            document.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Деактивирован документ ID {document_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка деактивации документа: {e}")
            raise
    
    def get_document_version_history(self, document_type: DocumentType) -> List[Dict[str, Any]]:
        """Получение истории версий документа"""
        documents = self.db.query(LegalDocument).filter(
            LegalDocument.type == document_type
        ).order_by(desc(LegalDocument.effective_date)).all()
        
        return [
            {
                "id": doc.id,
                "version": doc.version,
                "title": doc.title,
                "is_active": doc.is_active,
                "effective_date": doc.effective_date,
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    
    def accept_document(self, user_id: int, document_id: int, ip_address: str = None, user_agent: str = None) -> bool:
        """Принятие документа пользователем"""
        try:
            # Проверяем, что документ существует и активен
            document = self.get_document_by_id(document_id)
            if not document or not document.is_active:
                return False
            
            # Проверяем, не принял ли пользователь уже этот документ
            existing_acceptance = self.db.query(UserDocumentAcceptance).filter(
                and_(
                    UserDocumentAcceptance.user_id == user_id,
                    UserDocumentAcceptance.document_id == document_id
                )
            ).first()
            
            if existing_acceptance:
                logger.info(f"Пользователь {user_id} уже принял документ {document_id}")
                return True
            
            # Создаем запись о принятии
            acceptance = UserDocumentAcceptance(
                user_id=user_id,
                document_id=document_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(acceptance)
            self.db.commit()
            
            logger.info(f"Пользователь {user_id} принял документ {document_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка принятия документа: {e}")
            raise
    
    def get_user_documents_status(self, user_id: int) -> Dict[str, Any]:
        """Получение статуса документов пользователя"""
        try:
            # Получаем все активные документы
            active_documents = self.db.query(LegalDocument).filter(
                LegalDocument.is_active == True
            ).all()
            
            # Получаем принятые пользователем документы
            accepted_documents = self.db.query(UserDocumentAcceptance).filter(
                UserDocumentAcceptance.user_id == user_id
            ).all()
            
            accepted_ids = {acc.document_id for acc in accepted_documents}
            
            # Формируем статус
            documents_status = []
            pending_acceptance = []
            
            for doc in active_documents:
                if doc.requires_acceptance:
                    if doc.id in accepted_ids:
                        status = "accepted"
                    else:
                        status = "pending"
                        pending_acceptance.append(doc.id)
                else:
                    status = "not_required"
                
                documents_status.append({
                    "id": doc.id,
                    "type": doc.type.value,
                    "version": doc.version,
                    "title": doc.title,
                    "status": status,
                    "effective_date": doc.effective_date
                })
            
            return {
                "user_id": user_id,
                "documents": documents_status,
                "pending_acceptance": pending_acceptance,
                "total_documents": len(active_documents),
                "accepted_documents": len(accepted_ids),
                "pending_documents": len(pending_acceptance)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса документов: {e}")
            raise
    
    def get_document_acceptance_stats(self, document_id: int) -> Dict[str, Any]:
        """Получение статистики принятия документа"""
        try:
            total_acceptances = self.db.query(UserDocumentAcceptance).filter(
                UserDocumentAcceptance.document_id == document_id
            ).count()
            
            recent_acceptances = self.db.query(UserDocumentAcceptance).filter(
                UserDocumentAcceptance.document_id == document_id
            ).order_by(desc(UserDocumentAcceptance.accepted_at)).limit(10).all()
            
            return {
                "document_id": document_id,
                "total_acceptances": total_acceptances,
                "recent_acceptances": [
                    {
                        "user_id": acc.user_id,
                        "accepted_at": acc.accepted_at,
                        "ip_address": acc.ip_address
                    }
                    for acc in recent_acceptances
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики документа: {e}")
            raise
