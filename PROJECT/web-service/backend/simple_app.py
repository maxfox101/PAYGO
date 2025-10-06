from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from pydantic import BaseModel
from typing import Optional, List

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="PayGo API",
    description="API для системы платежных терминалов PayGo",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
        "https://*.ngrok.io",
        "https://*.trycloudflare.com",
        "https://*.loca.lt",
        "*"  # Временно для тестирования
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Тестовые данные
MOCK_USER = {
    "id": 1,
    "email": "nzosim@sfedu.ru",
    "phone": "+7 (928) 528-45-27",
    "full_name": "Никита Зосим Кириллович",
    "role": "user",
    "is_active": True,
    "balance": 192857.43
}

MOCK_CARDS = [
    {
        "id": 1,
        "masked_number": "**** **** **** 5678",
        "bank_name": "Т-банк",
        "card_type": "debit",
        "is_primary": True,
        "expires_at": "2027-04-30",
        "is_active": True
    },
    {
        "id": 2,
        "masked_number": "**** **** **** 1234",
        "bank_name": "ВТБ",
        "card_type": "debit",
        "is_primary": False,
        "expires_at": "2026-08-31",
        "is_active": True
    },
    {
        "id": 3,
        "masked_number": "**** **** **** 9876",
        "bank_name": "Альфа-банк",
        "card_type": "credit",
        "is_primary": False,
        "expires_at": "2025-11-30",
        "is_active": True
    }
]

MOCK_TRANSACTIONS = [
    {
        "id": 1,
        "amount": -2450.00,
        "currency": "RUB",
        "status": "completed",
        "description": "Магнит",
        "payment_method": "nfc",
        "created_at": "2025-08-08T14:23:00",
        "card_info": {"masked_number": "**** 5678", "bank_name": "Т-банк"},
        "terminal_info": {"name": "ТЦ Горизонт"}
    },
    {
        "id": 2,
        "amount": -45.00,
        "currency": "RUB",
        "status": "completed",
        "description": "Транспорт",
        "payment_method": "nfc",
        "created_at": "2025-08-08T09:15:00",
        "card_info": {"masked_number": "**** 5678", "bank_name": "Т-банк"},
        "terminal_info": {"name": "Автобус №15"}
    },
    {
        "id": 3,
        "amount": -320.00,
        "currency": "RUB",
        "status": "completed",
        "description": "Старбакс",
        "payment_method": "qr_code",
        "created_at": "2025-08-07T16:42:00",
        "card_info": {"masked_number": "**** 1234", "bank_name": "ВТБ"},
        "terminal_info": {"name": "Кафе Старбакс"}
    },
    {
        "id": 4,
        "amount": 15000.00,
        "currency": "RUB",
        "status": "completed",
        "description": "Пополнение",
        "payment_method": "transfer",
        "created_at": "2025-08-06T10:30:00",
        "card_info": {"masked_number": "**** 5678", "bank_name": "Т-банк"},
        "terminal_info": {"name": "Банкомат"}
    }
]

MOCK_TERMINALS = [
    {
        "id": 1,
        "serial_number": "PAYGO_001",
        "name": "Терминал №1",
        "location": "ТЦ Горизонт",
        "address": "ул. Пушкинская, 10, Ростов-на-Дону",
        "status": "online",
        "model": "PayGo-Pro-2025",
        "manufacturer": "PayGo Systems",
        "last_ping": "2025-08-08T14:30:00"
    },
    {
        "id": 2,
        "serial_number": "PAYGO_002",
        "name": "Терминал №2",
        "location": "Супермаркет Магнит",
        "address": "пр. Ленина, 45, Ростов-на-Дону",
        "status": "online",
        "model": "PayGo-Lite-2025",
        "manufacturer": "PayGo Systems",
        "last_ping": "2025-08-08T14:25:00"
    },
    {
        "id": 3,
        "serial_number": "PAYGO_003",
        "name": "Терминал №3",
        "location": "Кафе Старбакс",
        "address": "ул. Большая Садовая, 123, Ростов-на-Дону",
        "status": "offline",
        "model": "PayGo-Pro-2025",
        "manufacturer": "PayGo Systems",
        "last_ping": "2025-08-08T12:15:00"
    }
]

class BankCard(BaseModel):
    id: int
    card_number: str
    cardholder_name: str
    expiry_month: int
    expiry_year: int
    cvv: str
    bank_name: str
    card_type: str  # visa, mastercard, mir
    is_default: bool = False
    is_active: bool = True
    created_at: str

class AddCardRequest(BaseModel):
    card_number: str
    cardholder_name: str
    expiry_month: int
    expiry_year: int
    cvv: str
    bank_name: str
    card_type: str

class UserProfile(BaseModel):
    id: int
    phone: str
    first_name: str
    last_name: str
    middle_name: Optional[str]
    email: Optional[str]
    balance: float
    registration_date: str
    is_verified: bool
    cards: List[BankCard] = []
    total_transactions: int
    last_login: str

# Базовые эндпоинты
@app.get("/api/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "PayGo Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info")
async def get_info():
    """Информация о системе"""
    return {
        "name": "PayGo",
        "description": "Система платежных терминалов",
        "version": "1.0.0",
        "features": [
            "NFC платежи",
            "QR-коды",
            "Биометрическая аутентификация",
            "Интеграция с банками РФ",
            "Веб-интерфейс управления"
        ]
    }

# Эндпоинты для аутентификации
@app.post("/api/v1/auth/login")
async def login_user(credentials: dict):
    """Аутентификация пользователя"""
    return {
        "access_token": f"jwt_token_demo_{credentials.get('email', 'user')}",
        "token_type": "bearer",
        "user": MOCK_USER
    }

@app.get("/api/v1/users/me")
async def get_current_user():
    """Получение информации о текущем пользователе"""
    return MOCK_USER

@app.get("/api/v1/users/profile")
def get_user_profile(token: str = None):
    """Получить полный профиль пользователя с картами и статистикой"""
    if not token or token not in sessions_db:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user = users_db[user_id]
    
    # Получаем статистику пользователя
    user_transactions = [t for t in transactions_db.values() if t.get('user_id') == user_id]
    
    profile = {
        "id": user_id,
        "phone": user['phone'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "middle_name": user.get('middle_name'),
        "email": user.get('email'),
        "balance": user.get('balance', 0.0),
        "registration_date": user['registration_date'],
        "is_verified": user.get('is_verified', True),
        "cards": user.get('cards', []),
        "total_transactions": len(user_transactions),
        "last_login": datetime.now().isoformat(),
        "statistics": {
            "total_spent": sum(t['amount'] for t in user_transactions if t['transaction_type'] == 'payment'),
            "total_received": sum(t['amount'] for t in user_transactions if t['transaction_type'] == 'transfer'),
            "favorite_terminals": list(set(t.get('terminal_id', 'Unknown') for t in user_transactions))
        }
    }
    
    return profile

# Эндпоинты для карт
@app.get("/api/v1/cards")
async def get_user_cards():
    """Получение карт пользователя"""
    return MOCK_CARDS

@app.post("/api/v1/cards")
async def add_user_card(card_data: dict):
    """Добавление новой карты"""
    new_card = {
        "id": len(MOCK_CARDS) + 1,
        "masked_number": card_data.get("masked_number", "**** **** **** 0000"),
        "bank_name": card_data.get("bank_name", "Новый банк"),
        "card_type": card_data.get("card_type", "debit"),
        "is_primary": card_data.get("is_primary", False),
        "expires_at": card_data.get("expires_at", "2030-12-31"),
        "is_active": True
    }
    MOCK_CARDS.append(new_card)
    return new_card

@app.post("/api/v1/cards/add")
def add_bank_card(request: AddCardRequest, token: str = None):
    """Добавить новую банковскую карту"""
    if not token or token not in sessions_db:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Генерируем ID для новой карты
    card_id = len(users_db[user_id].get('cards', [])) + 1
    
    new_card = {
        "id": card_id,
        "card_number": request.card_number[-4:],  # Показываем только последние 4 цифры
        "cardholder_name": request.cardholder_name,
        "expiry_month": request.expiry_month,
        "expiry_year": request.expiry_year,
        "cvv": "***",  # Не показываем CVV
        "bank_name": request.bank_name,
        "card_type": request.card_type,
        "is_default": len(users_db[user_id].get('cards', [])) == 0,  # Первая карта по умолчанию
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    if 'cards' not in users_db[user_id]:
        users_db[user_id]['cards'] = []
    
    users_db[user_id]['cards'].append(new_card)
    
    return {"message": "Карта успешно добавлена", "card": new_card}

@app.get("/api/v1/cards/list")
def get_user_cards(token: str = None):
    """Получить список карт пользователя"""
    if not token or token not in sessions_db:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {"cards": users_db[user_id].get('cards', [])}

@app.delete("/api/v1/cards/{card_id}")
def delete_bank_card(card_id: int, token: str = None):
    """Удалить банковскую карту"""
    if not token or token not in sessions_db:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    cards = users_db[user_id].get('cards', [])
    card_index = next((i for i, card in enumerate(cards) if card['id'] == card_id), None)
    
    if card_index is None:
        raise HTTPException(status_code=404, detail="Карта не найдена")
    
    deleted_card = cards.pop(card_index)
    
    # Если удаляемая карта была по умолчанию, назначаем первую доступную
    if deleted_card['is_default'] and cards:
        cards[0]['is_default'] = True
    
    return {"message": "Карта успешно удалена"}

@app.put("/api/v1/cards/{card_id}/default")
def set_default_card(card_id: int, token: str = None):
    """Установить карту по умолчанию"""
    if not token or token not in sessions_db:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    cards = users_db[user_id].get('cards', [])
    
    # Сбрасываем все карты с флагом default
    for card in cards:
        card['is_default'] = False
    
    # Устанавливаем нужную карту как default
    target_card = next((card for card in cards if card['id'] == card_id), None)
    if target_card:
        target_card['is_default'] = True
        return {"message": f"Карта {target_card['card_number']} установлена по умолчанию"}
    else:
        raise HTTPException(status_code=404, detail="Карта не найдена")

# Эндпоинты для терминалов
@app.get("/api/v1/terminals")
async def get_terminals():
    """Получение списка терминалов"""
    return MOCK_TERMINALS

@app.get("/api/v1/terminals/{terminal_id}")
async def get_terminal(terminal_id: int):
    """Получение информации о терминале"""
    terminal = next((t for t in MOCK_TERMINALS if t["id"] == terminal_id), None)
    if not terminal:
        raise HTTPException(status_code=404, detail="Терминал не найден")

    # Добавляем статистику
    terminal_stats = {
        "total_transactions": 156,
        "total_amount": 234567.89,
        "successful_transactions": 152
    }

    return {**terminal, "statistics": terminal_stats}

# Эндпоинты для транзакций
@app.get("/api/v1/transactions")
async def get_transactions(limit: int = 50, offset: int = 0):
    """Получение списка транзакций"""
    start = offset
    end = offset + limit
    return MOCK_TRANSACTIONS[start:end]

@app.post("/api/v1/transactions")
async def create_transaction(transaction_data: dict):
    """Создание новой транзакции"""
    new_transaction = {
        "id": len(MOCK_TRANSACTIONS) + 1,
        "amount": transaction_data.get("amount", 0),
        "currency": "RUB",
        "status": "pending",
        "description": transaction_data.get("description", "Новая транзакция"),
        "payment_method": transaction_data.get("payment_method", "nfc"),
        "created_at": datetime.now().isoformat(),
        "card_info": {"masked_number": "**** 5678", "bank_name": "Т-банк"},
        "terminal_info": {"name": "PayGo Terminal"}
    }
    MOCK_TRANSACTIONS.append(new_transaction)
    return new_transaction

# Эндпоинты для статистики
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Получение статистики для дашборда"""
    return {
        "total_users": 1247,
        "total_terminals": len(MOCK_TERMINALS),
        "total_transactions": len(MOCK_TRANSACTIONS),
        "total_amount": sum(abs(t["amount"]) for t in MOCK_TRANSACTIONS),
        "recent_transactions": len([t for t in MOCK_TRANSACTIONS if t["created_at"] > "2025-08-07"]),
        "recent_amount": sum(abs(t["amount"]) for t in MOCK_TRANSACTIONS if t["created_at"] > "2025-08-07"),
        "terminal_status": {
            "online": len([t for t in MOCK_TERMINALS if t["status"] == "online"]),
            "offline": len([t for t in MOCK_TERMINALS if t["status"] == "offline"]),
            "maintenance": 0
        }
    }

# Эндпоинт для курсов валют
@app.get("/api/v1/currency/rates")
async def get_currency_rates():
    """Получение курсов валют"""
    return {
        "USD": {
            "rate": 91.45,
            "change": -0.23,
            "trend": "down"
        },
        "EUR": {
            "rate": 98.72,
            "change": 0.15,
            "trend": "up"
        },
        "CNY": {
            "rate": 12.63,
            "change": 0.42,
            "trend": "up"
        }
    }

# Обработчики ошибок
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Ресурс не найден", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Внутренняя ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Внутренняя ошибка сервера"}
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск PayGo Backend API...")
    print("📍 Доступен по адресу: http://localhost:8000")
    print("📖 API документация: http://localhost:8000/api/docs")
    uvicorn.run(
        "simple_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 