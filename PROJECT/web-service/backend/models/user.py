from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"                    # Обычный клиент
    ADMIN = "admin"                  # Администратор системы
    TERMINAL_OPERATOR = "terminal_operator"  # Операционист терминала
    FINANCE_MANAGER = "finance_manager"       # Финансовый менеджер
    SUPPORT_AGENT = "support_agent"           # Агент поддержки
    AUDITOR = "auditor"                       # Аудитор
    SYSTEM_OPERATOR = "system_operator"       # Системный оператор

class Permission(str, Enum):
    # Пользователи
    VIEW_OWN_PROFILE = "view_own_profile"
    EDIT_OWN_PROFILE = "edit_own_profile"
    MANAGE_OWN_CARDS = "manage_own_cards"
    VIEW_OWN_TRANSACTIONS = "view_own_transactions"
    
    # Операционисты
    MANAGE_TERMINALS = "manage_terminals"
    PROCESS_PAYMENTS = "process_payments"
    VIEW_TERMINAL_STATS = "view_terminal_stats"
    MANAGE_CASH = "manage_cash"
    
    # Финансовые менеджеры
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    MANAGE_REFUNDS = "manage_refunds"
    VIEW_ALL_TRANSACTIONS = "view_all_transactions"
    MANAGE_COMMISSIONS = "manage_commissions"
    
    # Администраторы
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    SYSTEM_CONFIGURATION = "system_configuration"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    MANAGE_BACKUPS = "manage_backups"
    
    # Аудиторы
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_DATA = "export_data"
    VIEW_COMPLIANCE_REPORTS = "view_compliance_reports"
    
    # Системные операторы
    MONITOR_SYSTEM = "monitor_system"
    MANAGE_UPDATES = "manage_updates"
    RESTART_SERVICES = "restart_services"

class BiometricType(str, Enum):
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"

class UserBase(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    date_of_birth: Optional[datetime] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    permissions: List[Permission] = []

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    permissions: Optional[List[Permission]] = None

class BiometricTemplate(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: BiometricType
    template_data: str  # Зашифрованные биометрические данные
    created_at: datetime
    is_active: bool = True

class UserNotificationSettings(BaseModel):
    user_id: str
    push_notifications: bool = True
    sms_notifications: bool = True
    email_notifications: bool = False
    transaction_alerts: bool = True
    security_alerts: bool = True
    system_updates: bool = False
    marketing_notifications: bool = False

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    is_locked: bool = False
    two_factor_enabled: bool = False
    notification_settings: Optional[UserNotificationSettings] = None
    biometric_templates: List[BiometricTemplate] = []
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class PasswordReset(BaseModel):
    email: EmailStr

class BiometricAuth(BaseModel):
    user_id: str
    biometric_type: BiometricType
    template_data: str

# Класс для управления правами доступа
class PermissionManager:
    @staticmethod
    def get_role_permissions(role: UserRole) -> List[Permission]:
        """Получение прав доступа для роли"""
        role_permissions = {
            UserRole.USER: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.MANAGE_OWN_CARDS,
                Permission.VIEW_OWN_TRANSACTIONS
            ],
            UserRole.TERMINAL_OPERATOR: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.MANAGE_TERMINALS,
                Permission.PROCESS_PAYMENTS,
                Permission.VIEW_TERMINAL_STATS,
                Permission.MANAGE_CASH
            ],
            UserRole.FINANCE_MANAGER: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.VIEW_FINANCIAL_REPORTS,
                Permission.MANAGE_REFUNDS,
                Permission.VIEW_ALL_TRANSACTIONS,
                Permission.MANAGE_COMMISSIONS
            ],
            UserRole.SUPPORT_AGENT: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.VIEW_OWN_TRANSACTIONS
            ],
            UserRole.AUDITOR: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.VIEW_AUDIT_LOGS,
                Permission.EXPORT_DATA,
                Permission.VIEW_COMPLIANCE_REPORTS
            ],
            UserRole.SYSTEM_OPERATOR: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.MONITOR_SYSTEM,
                Permission.MANAGE_UPDATES,
                Permission.RESTART_SERVICES
            ],
            UserRole.ADMIN: [
                Permission.VIEW_OWN_PROFILE,
                Permission.EDIT_OWN_PROFILE,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.SYSTEM_CONFIGURATION,
                Permission.VIEW_SYSTEM_LOGS,
                Permission.MANAGE_BACKUPS,
                Permission.VIEW_ALL_TRANSACTIONS,
                Permission.MANAGE_TERMINALS,
                Permission.PROCESS_PAYMENTS,
                Permission.VIEW_FINANCIAL_REPORTS,
                Permission.MANAGE_REFUNDS,
                Permission.MANAGE_COMMISSIONS,
                Permission.VIEW_AUDIT_LOGS,
                Permission.EXPORT_DATA,
                Permission.VIEW_COMPLIANCE_REPORTS,
                Permission.MONITOR_SYSTEM,
                Permission.MANAGE_UPDATES,
                Permission.RESTART_SERVICES
            ]
        }
        
        return role_permissions.get(role, [])
    
    @staticmethod
    def has_permission(user_permissions: List[Permission], required_permission: Permission) -> bool:
        """Проверка наличия права доступа"""
        return required_permission in user_permissions
    
    @staticmethod
    def has_any_permission(user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """Проверка наличия хотя бы одного права из списка"""
        return any(perm in user_permissions for perm in required_permissions)
    
    @staticmethod
    def has_all_permissions(user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """Проверка наличия всех прав из списка"""
        return all(perm in user_permissions for perm in required_permissions) 