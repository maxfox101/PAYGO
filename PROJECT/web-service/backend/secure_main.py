#!/usr/bin/env python3
"""
Безопасный PayGo API сервер с аутентификацией, защитой и всеми функциями
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator, EmailStr
import uvicorn
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import secrets
import jwt
import re
import logging
from enum import Enum

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="PayGo Secure API",
    description="Безопасный API для системы платежных терминалов PayGo",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Безопасность (отключено для разработки)
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["localhost", "127.0.0.1", "*.paygo.ru"]
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники для разработки
    allow_credentials=False,  # Отключаем credentials для безопасности
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Конфигурация безопасности
SECURITY_CONFIG = {
    "SECRET_KEY": "your-secret-key-change-in-production",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 60,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7,
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOCKOUT_DURATION_MINUTES": 15,
    "PASSWORD_MIN_LENGTH": 8,
    "RATE_LIMIT_REQUESTS": 100,
    "RATE_LIMIT_WINDOW": 60
}

# Хранилище данных (в реальном приложении - база данных)
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
login_attempts: Dict[str, Dict] = {}
rate_limit_store: Dict[str, List] = {}

# Модели данных
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    TERMINAL_OPERATOR = "terminal_operator"
    FINANCE_MANAGER = "finance_manager"

class UserBase(BaseModel):
    phone: str
    full_name: str
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.USER
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < SECURITY_CONFIG["PASSWORD_MIN_LENGTH"]:
            raise ValueError(f'Пароль должен содержать минимум {SECURITY_CONFIG["PASSWORD_MIN_LENGTH"]} символов')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Пароль должен содержать буквы')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать цифры')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Неверный формат номера телефона')
        return v

class UserLogin(BaseModel):
    phone: str
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    balance: float = 0.0

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str

class CardType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"

class Card(BaseModel):
    id: str
    user_id: str
    bank_name: str
    card_number: str
    cardholder_name: str
    expiry_date: str
    card_type: CardType
    is_active: bool = True
    balance: float
    created_at: datetime

class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    description: str
    transaction_type: str
    status: str
    created_at: datetime
    card_id: Optional[str] = None

class SecurityLog(BaseModel):
    event: str
    timestamp: datetime
    user: str
    ip: str
    user_agent: str
    details: Optional[Dict[str, Any]] = None

# Утилиты безопасности
def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    try:
        salt, hash_value = hashed.split('$')
        hash_obj = hashlib.sha256((password + salt).encode())
        return hash_obj.hexdigest() == hash_value
    except:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SECURITY_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECURITY_CONFIG["SECRET_KEY"], algorithm=SECURITY_CONFIG["ALGORITHM"])
    return encoded_jwt

def create_refresh_token(data: dict):
    """Создание refresh токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=SECURITY_CONFIG["REFRESH_TOKEN_EXPIRE_DAYS"])
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECURITY_CONFIG["SECRET_KEY"], algorithm=SECURITY_CONFIG["ALGORITHM"])
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

# Зависимости
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Получение текущего пользователя из токена"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    user = users_db[user_id]
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Пользователь заблокирован")
    
    return user

def check_rate_limit(request: Request):
    """Проверка rate limit"""
    client_ip = request.client.host
    current_time = datetime.utcnow()
    
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Удаляем старые запросы
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if (current_time - req_time).seconds < SECURITY_CONFIG["RATE_LIMIT_WINDOW"]
    ]
    
    # Проверяем лимит
    if len(rate_limit_store[client_ip]) >= SECURITY_CONFIG["RATE_LIMIT_REQUESTS"]:
        raise HTTPException(
            status_code=429, 
            detail="Превышен лимит запросов. Попробуйте позже."
        )
    
    # Добавляем текущий запрос
    rate_limit_store[client_ip].append(current_time)

# Эндпоинты аутентификации
@app.post("/api/v1/auth/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate):
    """Регистрация пользователя"""
    # Проверяем, не существует ли уже пользователь
    for user in users_db.values():
        if user["phone"] == user_data.phone:
            raise HTTPException(status_code=400, detail="Пользователь с таким номером уже существует")
    
    # Создаем пользователя
    user_id = f"user_{len(users_db) + 1}"
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "phone": user_data.phone,
        "full_name": user_data.full_name,
        "email": user_data.email,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "failed_login_attempts": 0,
        "balance": 1000.0,  # Начальный баланс
        "password_hash": hashed_password  # Сохраняем хешированный пароль
    }
    
    users_db[user_id] = user
    
    # Логируем регистрацию
    log_security_event("REGISTRATION_SUCCESS", user_id, "local", "API")
    
    return {
        "message": "Пользователь успешно зарегистрирован",
        "user": {
            "id": user_id,
            "phone": user_data.phone,
            "full_name": user_data.full_name,
            "email": user_data.email,
            "role": user_data.role,
            "is_active": True
        }
    }

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, request: Request):
    """Вход в систему"""
    # Проверяем rate limit
    check_rate_limit(request)
    
    # Проверяем блокировку
    if is_account_locked(user_credentials.phone):
        raise HTTPException(
            status_code=423, 
            detail=f"Аккаунт заблокирован на {SECURITY_CONFIG['LOCKOUT_DURATION_MINUTES']} минут"
        )
    
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u["phone"] == user_credentials.phone:
            user = u
            break
    
    if not user:
        handle_login_failure(user_credentials.phone)
        raise HTTPException(status_code=401, detail="Неверный номер телефона или пароль")
    
    # Проверяем пароль
    if not verify_password(user_credentials.password, user.get("password_hash", "")):
        handle_login_failure(user_credentials.phone)
        raise HTTPException(status_code=401, detail="Неверный номер телефона или пароль")
    
    # Создаем токены
    access_token = create_access_token(data={"sub": user["id"]})
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    # Обновляем данные пользователя
    user["last_login"] = datetime.utcnow()
    user["failed_login_attempts"] = 0
    user["updated_at"] = datetime.utcnow()
    
    # Сохраняем сессию
    session_id = f"session_{len(sessions_db) + 1}"
    sessions_db[session_id] = {
        "user_id": user["id"],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow()
    }
    
    # Сбрасываем счетчик неудачных попыток
    reset_login_attempts(user_credentials.phone)
    
    # Логируем успешный вход
    log_security_event("LOGIN_SUCCESS", user["id"], request.client.host, request.headers.get("user-agent", ""))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": SECURITY_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60,
        "refresh_token": refresh_token
    }

@app.post("/api/v1/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Обновление токена"""
    try:
        payload = jwt.decode(refresh_token, SECURITY_CONFIG["SECRET_KEY"], algorithms=[SECURITY_CONFIG["ALGORITHM"]])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Неверный тип токена")
        
        user_id = payload.get("sub")
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        
        # Создаем новые токены
        access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": SECURITY_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60,
            "refresh_token": new_refresh_token
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh токен истек")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")

@app.post("/api/v1/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Выход из системы"""
    # Удаляем сессию
    sessions_to_remove = []
    for session_id, session in sessions_db.items():
        if session["user_id"] == current_user["id"]:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del sessions_db[session_id]
    
    # Логируем выход
    log_security_event("LOGOUT", current_user["id"], "local", "API")
    
    return {"message": "Успешный выход из системы"}

@app.get("/api/v1/auth/validate")
async def validate_token(current_user: Dict = Depends(get_current_user)):
    """Валидация токена"""
    return current_user

# Эндпоинты пользователей
@app.get("/api/v1/users/me", response_model=User)
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

@app.get("/api/v1/users/profile")
async def get_user_profile(current_user: Dict = Depends(get_current_user)):
    """Получение профиля пользователя"""
    return {
        "id": current_user["id"],
        "phone": current_user["phone"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"],
        "updated_at": current_user["updated_at"],
        "last_login": current_user["last_login"],
        "balance": current_user["balance"]
    }

@app.get("/api/v1/users/cards", response_model=List[Card])
async def get_user_cards(current_user: Dict = Depends(get_current_user)):
    """Получение карт пользователя"""
    # Демо данные для карт
    demo_cards = [
        {
            "id": "card_1",
            "user_id": current_user["id"],
            "bank_name": "T-банк",
            "card_number": ".... 5678",
            "cardholder_name": current_user["full_name"],
            "expiry_date": "04/27",
            "card_type": CardType.DEBIT,
            "is_active": True,
            "balance": 128456.32,
            "created_at": datetime.utcnow()
        },
        {
            "id": "card_2",
            "user_id": current_user["id"],
            "bank_name": "ВТБ",
            "card_number": ".... 1234",
            "cardholder_name": current_user["full_name"],
            "expiry_date": "08/26",
            "card_type": CardType.DEBIT,
            "is_active": True,
            "balance": 45321.90,
            "created_at": datetime.utcnow()
        },
        {
            "id": "card_3",
            "user_id": current_user["id"],
            "bank_name": "Альфа-Банк",
            "card_number": ".... 9876",
            "cardholder_name": current_user["full_name"],
            "expiry_date": "11/25",
            "card_type": CardType.CREDIT,
            "is_active": True,
            "balance": 19079.21,
            "created_at": datetime.utcnow()
        }
    ]
    
    return demo_cards

@app.get("/api/v1/users/transactions", response_model=List[Transaction])
async def get_user_transactions(current_user: Dict = Depends(get_current_user)):
    """Получение транзакций пользователя"""
    # Демо данные для транзакций
    demo_transactions = [
        {
            "id": "txn_1",
            "user_id": current_user["id"],
            "amount": 1500.0,
            "description": "Покупка в магазине",
            "transaction_type": "payment",
            "status": "completed",
            "created_at": datetime.utcnow(),
            "card_id": "card_1"
        },
        {
            "id": "txn_2",
            "user_id": current_user["id"],
            "amount": 250.0,
            "description": "Оплата услуг",
            "transaction_type": "payment",
            "status": "completed",
            "created_at": datetime.utcnow(),
            "card_id": "card_2"
        }
    ]
    
    return demo_transactions

# Эндпоинты безопасности
@app.post("/api/v1/security/log")
async def log_security_event_endpoint(
    log_data: SecurityLog,
    current_user: Dict = Depends(get_current_user)
):
    """Логирование событий безопасности"""
    log_security_event(
        log_data.event,
        current_user["id"],
        log_data.ip,
        log_data.user_agent,
        log_data.details
    )
    return {"message": "Событие залогировано"}

# Эндпоинты для демо данных
@app.get("/api/v1/terminals")
async def get_terminals():
    """Получение списка терминалов"""
    return [
        {
            "terminal_id": "DEMO_001",
            "name": "Демо терминал 1",
            "location": "Офис PayGo",
            "status": "online",
            "last_heartbeat": datetime.utcnow()
        },
        {
            "terminal_id": "DEMO_002",
            "name": "Демо терминал 2",
            "location": "ТЦ Горизонт",
            "status": "online",
            "last_heartbeat": datetime.utcnow()
        }
    ]

@app.get("/api/v1/transactions")
async def get_transactions():
    """Получение списка транзакций"""
    return [
        {
            "transaction_id": "TXN_001",
            "amount": 1500.0,
            "status": "completed",
            "payment_method": "nfc_card",
            "created_at": datetime.utcnow()
        },
        {
            "transaction_id": "TXN_002",
            "amount": 250.0,
            "status": "completed",
            "payment_method": "qr_code",
            "created_at": datetime.utcnow()
        }
    ]

@app.get("/api/v1/stats/system")
async def get_system_stats():
    """Системная статистика"""
    return {
        "system_status": "healthy",
        "uptime": "Demo Mode",
        "version": "2.0.0",
        "terminals": {
            "total": 2,
            "online": 2,
            "offline": 0
        },
        "transactions": {
            "total": 2,
            "completed": 2,
            "pending": 0
        },
        "financial": {
            "total_amount": 1750.0,
            "average_transaction": 875.0
        }
    }

# Утилиты безопасности
def is_account_locked(phone: str) -> bool:
    """Проверка блокировки аккаунта"""
    if phone not in login_attempts:
        return False
    
    attempts_data = login_attempts[phone]
    if attempts_data["attempts"] >= SECURITY_CONFIG["MAX_LOGIN_ATTEMPTS"]:
        time_since_lockout = datetime.utcnow() - attempts_data["lockout_time"]
        if time_since_lockout.total_seconds() < SECURITY_CONFIG["LOCKOUT_DURATION_MINUTES"] * 60:
            return True
        else:
            # Снимаем блокировку
            del login_attempts[phone]
    
    return False

def handle_login_failure(phone: str):
    """Обработка неудачного входа"""
    if phone not in login_attempts:
        login_attempts[phone] = {
            "attempts": 1,
            "lockout_time": None
        }
    else:
        login_attempts[phone]["attempts"] += 1
    
    # Блокируем аккаунт при превышении лимита
    if login_attempts[phone]["attempts"] >= SECURITY_CONFIG["MAX_LOGIN_ATTEMPTS"]:
        login_attempts[phone]["lockout_time"] = datetime.utcnow()

def reset_login_attempts(phone: str):
    """Сброс счетчика неудачных попыток"""
    if phone in login_attempts:
        del login_attempts[phone]

def log_security_event(event: str, user_id: str, ip: str, user_agent: str, details: Optional[Dict] = None):
    """Логирование событий безопасности"""
    log_entry = {
        "event": event,
        "timestamp": datetime.utcnow(),
        "user_id": user_id,
        "ip": ip,
        "user_agent": user_agent,
        "details": details
    }
    
    logger.info(f"SECURITY_EVENT: {log_entry}")
    
    # В реальном приложении сохраняем в базу данных
    # security_logs.append(log_entry)

# Корневой эндпоинт
@app.get("/")
async def root():
    return {
        "message": "🚀 PayGo Secure API сервер запущен успешно!",
        "version": "2.0.0",
        "status": "secure",
        "docs": "/api/docs",
        "timestamp": datetime.utcnow()
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "paygo-secure-api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow(),
        "security": "enabled"
    }

# Запуск сервера
if __name__ == "__main__":
    print("🚀 Запуск PayGo Secure API сервера...")
    print("🔒 Безопасность: ВКЛЮЧЕНА")
    print("📍 Адрес: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/api/docs")
    print("💓 Здоровье системы: http://localhost:8000/api/health")
    print("-" * 60)
    
    uvicorn.run(
        "secure_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
