from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
import re
import random
import time

app = FastAPI(
    title="PayGo API",
    description="API для системы платежей PayGo с регистрацией",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# В реальном приложении это должно быть в базе данных
users_db = {}
sms_codes_db = {}
sessions_db = {}

# Data Models
class PhoneRegisterRequest(BaseModel):
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        # Проверяем формат российского номера
        phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Неверный формат номера телефона')
        return v

class SMSVerifyRequest(BaseModel):
    phone: str
    code: str

class UserRegistrationRequest(BaseModel):
    phone: str
    code: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str

class User(BaseModel):
    id: int
    phone: str
    full_name: str
    email: Optional[str]
    balance: float
    registration_date: str
    is_verified: bool = True

class Transaction(BaseModel):
    id: int
    amount: float
    description: str
    created_at: str
    transaction_type: str
    status: str

class Card(BaseModel):
    id: int
    bank_name: str
    card_number: str
    cardholder_name: str
    expiry_date: str
    is_active: bool

# Утилиты
def normalize_phone(phone: str) -> str:
    """Нормализация номера телефона к формату +7XXXXXXXXXX"""
    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Приводим к формату +7XXXXXXXXXX
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    elif digits.startswith('7') and len(digits) == 11:
        pass
    elif len(digits) == 10:
        digits = '7' + digits
    
    return '+' + digits

def generate_sms_code() -> str:
    """Генерация 4-значного SMS кода"""
    return str(random.randint(1000, 9999))

def send_sms(phone: str, code: str) -> bool:
    """Имитация отправки SMS (в реальном приложении здесь будет API SMS-провайдера)"""
    print(f"📱 SMS на {phone}: Ваш код подтверждения PayGo: {code}")
    return True

def generate_session_token() -> str:
    """Генерация токена сессии"""
    return secrets.token_urlsafe(32)

def get_current_user(token: str = None):
    """Получение текущего пользователя по токену"""
    if not token or token not in sessions_db:
        return None
    
    session = sessions_db[token]
    if session['expires'] < datetime.now():
        del sessions_db[token]
        return None
    
    phone = session['phone']
    return users_db.get(phone)

# Sample data
sample_transactions = [
    Transaction(
        id=1,
        amount=-2450.00,
        description="Магнит",
        created_at="2025-08-08T14:23:00",
        transaction_type="purchase",
        status="completed"
    ),
    Transaction(
        id=2,
        amount=-45.00,
        description="Транспорт",
        created_at="2025-08-08T09:15:00",
        transaction_type="transport",
        status="completed"
    ),
    Transaction(
        id=3,
        amount=15000.00,
        description="Зарплата",
        created_at="2025-08-07T16:00:00",
        transaction_type="income",
        status="completed"
    )
]

sample_cards = [
    Card(
        id=1,
        bank_name="Т‑Банк",
        card_number="**** **** **** 1234",
        cardholder_name="NIKITA ZOSIM",
        expiry_date="12/28",
        is_active=True
    ),
    Card(
        id=2,
        bank_name="ВТБ",
        card_number="**** **** **** 5678",
        cardholder_name="NIKITA ZOSIM",
        expiry_date="10/27",
        is_active=True
    )
]

# API Endpoints

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PayGo Backend API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": ["registration", "sms_verification", "authentication"]
    }

# Регистрация и аутентификация

@app.post("/api/v1/auth/register/phone")
def register_phone(request: PhoneRegisterRequest):
    """Шаг 1: Отправка SMS кода на номер телефона"""
    try:
        normalized_phone = normalize_phone(request.phone)
        
        # Генерируем код
        sms_code = generate_sms_code()
        
        # Сохраняем код с временем истечения (5 минут)
        sms_codes_db[normalized_phone] = {
            'code': sms_code,
            'expires': datetime.now() + timedelta(minutes=5),
            'attempts': 0
        }
        
        # Отправляем SMS
        if send_sms(normalized_phone, sms_code):
            return {
                "success": True,
                "message": "SMS код отправлен",
                "phone": normalized_phone,
                "expires_in": 300  # 5 минут в секундах
            }
        else:
            raise HTTPException(status_code=500, detail="Ошибка отправки SMS")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/verify/sms")
def verify_sms_code(request: SMSVerifyRequest):
    """Шаг 2: Проверка SMS кода"""
    try:
        normalized_phone = normalize_phone(request.phone)
        
        if normalized_phone not in sms_codes_db:
            raise HTTPException(status_code=400, detail="Код не найден или истек")
        
        sms_data = sms_codes_db[normalized_phone]
        
        # Проверяем истечение времени
        if sms_data['expires'] < datetime.now():
            del sms_codes_db[normalized_phone]
            raise HTTPException(status_code=400, detail="Код истек")
        
        # Проверяем количество попыток
        if sms_data['attempts'] >= 3:
            del sms_codes_db[normalized_phone]
            raise HTTPException(status_code=400, detail="Превышено количество попыток")
        
        # Проверяем код
        if sms_data['code'] != request.code:
            sms_data['attempts'] += 1
            raise HTTPException(status_code=400, detail="Неверный код")
        
        # Код верный - удаляем из временного хранилища
        del sms_codes_db[normalized_phone]
        
        # Проверяем, существует ли пользователь
        user_exists = normalized_phone in users_db
        
        return {
            "success": True,
            "verified": True,
            "user_exists": user_exists,
            "phone": normalized_phone
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/register/complete")
def complete_registration(request: UserRegistrationRequest):
    """Шаг 3: Завершение регистрации нового пользователя"""
    try:
        normalized_phone = normalize_phone(request.phone)
        
        # Проверяем, что пользователь уже не существует
        if normalized_phone in users_db:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        
        # Создаем нового пользователя
        full_name = f"{request.last_name} {request.first_name}"
        if request.middle_name:
            full_name += f" {request.middle_name}"
        
        user = User(
            id=len(users_db) + 1,
            phone=normalized_phone,
            full_name=full_name,
            email=request.email,
            balance=0.0,
            registration_date=datetime.now().isoformat(),
            is_verified=True
        )
        
        users_db[normalized_phone] = user
        
        # Создаем сессию
        token = generate_session_token()
        sessions_db[token] = {
            'phone': normalized_phone,
            'expires': datetime.now() + timedelta(days=30)
        }
        
        return {
            "success": True,
            "message": "Регистрация завершена успешно",
            "access_token": token,
            "token_type": "bearer",
            "user": user.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/login")
def login_user(request: LoginRequest):
    """Вход существующего пользователя"""
    try:
        normalized_phone = normalize_phone(request.phone)
        
        # Проверяем, что пользователь существует
        if normalized_phone not in users_db:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user = users_db[normalized_phone]
        
        # Создаем сессию
        token = generate_session_token()
        sessions_db[token] = {
            'phone': normalized_phone,
            'expires': datetime.now() + timedelta(days=30)
        }
        
        return {
            "success": True,
            "message": "Вход выполнен успешно",
            "access_token": token,
            "token_type": "bearer",
            "user": user.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/logout")
def logout_user(token: str):
    """Выход из системы"""
    if token in sessions_db:
        del sessions_db[token]
    
    return {"success": True, "message": "Выход выполнен успешно"}

# Защищенные эндпоинты

@app.get("/api/v1/users/me")
def get_current_user_info(token: str = None):
    """Получить информацию о текущем пользователе"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    return user

@app.get("/api/v1/transactions")
def get_user_transactions(token: str = None, limit: Optional[int] = 10):
    """Получить транзакции пользователя"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    return sample_transactions[:limit]

@app.get("/api/v1/cards")
def get_user_cards(token: str = None):
    """Получить карты пользователя"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    return sample_cards

@app.get("/api/v1/stats")
def get_user_statistics(token: str = None):
    """Получить статистику пользователя"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    return {
        "total_transactions": len(sample_transactions),
        "active_cards": len([card for card in sample_cards if card.is_active]),
        "current_balance": user.balance,
        "success_rate": 99.2
    }

# Публичные эндпоинты

@app.get("/api/v1/support/contacts")
def get_support_contacts():
    """Получить контакты поддержки"""
    return {
        "phone": "8 (800) 555-35-35",
        "email": "support@paygo.ru",
        "chat_available": True,
        "working_hours": "Круглосуточно",
        "response_time": "В течение 24 часов"
    }

@app.get("/api/v1/currency/rates")
def get_currency_rates():
    """Получить курсы валют"""
    return {
        "USD": {"rate": 91.83, "change": 0.09},
        "EUR": {"rate": 98.21, "change": -0.1},
        "CNY": {"rate": 12.78, "change": 0.08}
    }

# Демо эндпоинты для тестирования

@app.get("/api/v1/demo/users")
def get_demo_users():
    """Получить список всех пользователей (только для демо)"""
    return {
        "users": list(users_db.values()),
        "total": len(users_db)
    }

@app.get("/api/v1/demo/sessions")
def get_demo_sessions():
    """Получить активные сессии (только для демо)"""
    active_sessions = []
    current_time = datetime.now()
    
    for token, session in sessions_db.items():
        if session['expires'] > current_time:
            active_sessions.append({
                "token": token[:10] + "...",
                "phone": session['phone'],
                "expires": session['expires'].isoformat()
            })
    
    return {
        "active_sessions": active_sessions,
        "total": len(active_sessions)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск PayGo Backend API с регистрацией...")
    print("📖 Документация: http://localhost:8000/docs")
    print("🔍 Проверка здоровья: http://localhost:8000/api/health")
    print("📱 Регистрация: http://localhost:8000/api/v1/auth/register/phone")
    uvicorn.run(app, host="0.0.0.0", port=8000) 