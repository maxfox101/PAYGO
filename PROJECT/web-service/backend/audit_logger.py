import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class AuditEventType(str, Enum):
    # Аутентификация
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    
    # Управление пользователями
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    USER_LOCKED = "user_locked"
    USER_UNLOCKED = "user_unlocked"
    
    # Транзакции
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_UPDATED = "transaction_updated"
    TRANSACTION_CANCELLED = "transaction_cancelled"
    PAYMENT_PROCESSED = "payment_processed"
    REFUND_PROCESSED = "refund_processed"
    
    # Терминалы
    TERMINAL_ADDED = "terminal_added"
    TERMINAL_UPDATED = "terminal_updated"
    TERMINAL_REMOVED = "terminal_removed"
    TERMINAL_STATUS_CHANGED = "terminal_status_changed"
    
    # Карты
    CARD_ADDED = "card_added"
    CARD_UPDATED = "card_updated"
    CARD_REMOVED = "card_removed"
    CARD_BLOCKED = "card_blocked"
    
    # Система
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    SYSTEM_UPDATE = "system_update"
    SERVICE_RESTARTED = "service_restarted"
    
    # Безопасность
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCESS_DENIED = "access_denied"
    PERMISSION_VIOLATION = "permission_violation"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"

class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLogEntry(BaseModel):
    id: Optional[str] = None
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.INFO
    description: str
    details: Optional[Dict[str, Any]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

class AuditLogger:
    def __init__(self):
        self.log_file = "audit.log"
        self.max_log_size = 100 * 1024 * 1024  # 100MB
        self.max_log_files = 10
        
    async def log_event(self, entry: AuditLogEntry):
        """Логирование события аудита"""
        try:
            # Форматируем запись для лога
            log_entry = {
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "session_id": entry.session_id,
                "ip_address": entry.ip_address,
                "event_type": entry.event_type.value,
                "severity": entry.severity.value,
                "description": entry.description,
                "details": entry.details,
                "resource_type": entry.resource_type,
                "resource_id": entry.resource_id,
                "success": entry.success,
                "error_message": entry.error_message
            }
            
            # Записываем в файл
            log_line = json.dumps(log_entry, ensure_ascii=False) + "\n"
            
            async with asyncio.Lock():
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_line)
            
            # Также логируем в стандартный лог
            log_level = self._get_log_level(entry.severity)
            logger.log(log_level, f"AUDIT: {entry.description} | User: {entry.user_id} | Event: {entry.event_type.value}")
            
            # Проверяем размер лога и ротируем при необходимости
            await self._rotate_log_if_needed()
            
        except Exception as e:
            logger.error(f"❌ Ошибка записи аудита: {e}")
    
    def _get_log_level(self, severity: AuditSeverity) -> int:
        """Получение уровня логирования для стандартного логгера"""
        severity_map = {
            AuditSeverity.INFO: logging.INFO,
            AuditSeverity.WARNING: logging.WARNING,
            AuditSeverity.ERROR: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL
        }
        return severity_map.get(severity, logging.INFO)
    
    async def _rotate_log_if_needed(self):
        """Ротация логов при превышении размера"""
        try:
            if not await self._should_rotate():
                return
            
            # Переименовываем текущий лог
            import os
            for i in range(self.max_log_files - 1, 0, -1):
                old_name = f"{self.log_file}.{i}"
                new_name = f"{self.log_file}.{i + 1}"
                if os.path.exists(old_name):
                    os.rename(old_name, new_name)
            
            # Переименовываем текущий лог
            os.rename(self.log_file, f"{self.log_file}.1")
            
            # Создаем новый пустой лог
            with open(self.log_file, "w") as f:
                pass
                
            logger.info("🔄 Аудит лог ротирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка ротации аудит лога: {e}")
    
    async def _should_rotate(self) -> bool:
        """Проверка необходимости ротации"""
        try:
            import os
            if not os.path.exists(self.log_file):
                return False
            
            size = os.path.getsize(self.log_file)
            return size > self.max_log_size
            
        except Exception:
            return False
    
    async def log_user_action(self, 
                             user_id: str,
                             event_type: AuditEventType,
                             description: str,
                             details: Optional[Dict] = None,
                             severity: AuditSeverity = AuditSeverity.INFO,
                             success: bool = True,
                             error_message: Optional[str] = None,
                             **kwargs):
        """Упрощенное логирование действий пользователя"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            details=details,
            success=success,
            error_message=error_message,
            **kwargs
        )
        
        await self.log_event(entry)
    
    async def log_security_event(self,
                                event_type: AuditEventType,
                                description: str,
                                user_id: Optional[str] = None,
                                ip_address: Optional[str] = None,
                                details: Optional[Dict] = None):
        """Логирование событий безопасности"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            event_type=event_type,
            severity=AuditSeverity.WARNING,
            description=description,
            details=details,
            success=False
        )
        
        await self.log_event(entry)
    
    async def search_audit_logs(self,
                               user_id: Optional[str] = None,
                               event_type: Optional[AuditEventType] = None,
                               severity: Optional[AuditSeverity] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               limit: int = 100) -> List[AuditLogEntry]:
        """Поиск по аудит логам"""
        try:
            results = []
            count = 0
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if count >= limit:
                        break
                    
                    try:
                        log_data = json.loads(line.strip())
                        
                        # Применяем фильтры
                        if user_id and log_data.get("user_id") != user_id:
                            continue
                        if event_type and log_data.get("event_type") != event_type.value:
                            continue
                        if severity and log_data.get("severity") != severity.value:
                            continue
                        
                        # Фильтр по дате
                        if start_date or end_date:
                            log_timestamp = datetime.fromisoformat(log_data["timestamp"])
                            if start_date and log_timestamp < start_date:
                                continue
                            if end_date and log_timestamp > end_date:
                                continue
                        
                        # Создаем объект записи
                        entry = AuditLogEntry(
                            id=str(count),
                            timestamp=datetime.fromisoformat(log_data["timestamp"]),
                            user_id=log_data.get("user_id"),
                            session_id=log_data.get("session_id"),
                            ip_address=log_data.get("ip_address"),
                            user_agent=log_data.get("user_agent"),
                            event_type=AuditEventType(log_data["event_type"]),
                            severity=AuditSeverity(log_data["severity"]),
                            description=log_data["description"],
                            details=log_data.get("details"),
                            resource_type=log_data.get("resource_type"),
                            resource_id=log_data.get("resource_id"),
                            success=log_data.get("success", True),
                            error_message=log_data.get("error_message")
                        )
                        
                        results.append(entry)
                        count += 1
                        
                    except json.JSONDecodeError:
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска по аудит логам: {e}")
            return []

# Глобальный экземпляр аудит логгера
audit_logger = AuditLogger()

# Декоратор для автоматического логирования действий
def audit_log(event_type: AuditEventType, description: str, severity: AuditSeverity = AuditSeverity.INFO):
    """Декоратор для автоматического логирования действий функций"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                # Выполняем функцию
                result = await func(*args, **kwargs)
                
                # Логируем успешное выполнение
                await audit_logger.log_user_action(
                    user_id=kwargs.get("user_id", "system"),
                    event_type=event_type,
                    description=description,
                    severity=severity,
                    success=True,
                    details={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                )
                
                return result
                
            except Exception as e:
                # Логируем ошибку
                await audit_logger.log_user_action(
                    user_id=kwargs.get("user_id", "system"),
                    event_type=event_type,
                    description=f"{description} - ОШИБКА: {str(e)}",
                    severity=AuditSeverity.ERROR,
                    success=False,
                    error_message=str(e),
                    details={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                )
                raise
        
        return wrapper
    return decorator

