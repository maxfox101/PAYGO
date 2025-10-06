from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import asyncio
import logging

# Импорты для работы с БД
from database import init_db, close_db, get_database, Database
from models.user import User, UserCreate, UserLogin, UserResponse
from models.terminal import Terminal, TerminalCreate, TerminalResponse
from models.transaction import Transaction, TransactionCreate, TransactionResponse
from models.card import Card, CardCreate, CardResponse

# Импорты для правовых документов
from routers.legal_documents import router as legal_documents_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Контекстный менеджер для жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске
    logger.info("🚀 Запуск PayGo Backend...")
    await init_db()
    logger.info("✅ База данных инициализирована")
    
    yield
    
    # Очистка при завершении
    logger.info("🛑 Завершение работы PayGo Backend...")
    await close_db()
    logger.info("✅ Соединение с БД закрыто")

# Создание приложения FastAPI
app = FastAPI(
    title="PayGo API",
    description="API для системы платежных терминалов PayGo",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить конкретными доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для доверенных хостов
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # В продакшене ограничить
)

# Схема аутентификации
security = HTTPBearer()

# Dependency для получения базы данных
async def get_db():
    async with get_database() as database:
        yield database

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = asyncio.get_event_loop().time()
    response = await call_next(request)
    process_time = asyncio.get_event_loop().time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    return response

# Базовые эндпоинты
@app.get("/api/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "PayGo Backend",
        "version": "1.0.0"
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

# Эндпоинты для пользователей
@app.post("/api/v1/users/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Database = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await db.fetch_one(
            "SELECT id FROM users WHERE email = $1 OR phone = $2",
            user_data.email, user_data.phone
        )
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email или телефоном уже существует"
            )
        
        # Создаем пользователя
        user_id = await db.fetch_val(
            """
            INSERT INTO users (email, phone, full_name, hashed_password)
            VALUES ($1, $2, $3, $4) RETURNING id
            """,
            user_data.email,
            user_data.phone,
            user_data.full_name,
            f"$2b$12$hashed_{user_data.email}"  # В реальности нужно хешировать
        )
        
        return UserResponse(
            id=user_id,
            email=user_data.email,
            phone=user_data.phone,
            full_name=user_data.full_name,
            role="user",
            is_active=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/api/v1/auth/login")
async def login_user(
    credentials: UserLogin,
    db: Database = Depends(get_db)
):
    """Аутентификация пользователя"""
    try:
        user = await db.fetch_one(
            "SELECT * FROM users WHERE email = $1 AND is_active = true",
            credentials.email
        )
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Неверные учетные данные"
            )
        
        # В реальности здесь проверяем хеш пароля
        return {
            "access_token": f"jwt_token_for_{user['email']}",
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/api/v1/users/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    # Здесь должна быть проверка JWT токена
    user = await db.fetch_one(
        "SELECT * FROM users WHERE email = $1",
        "nzosim@sfedu.ru"  # Заглушка
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "phone": user["phone"],
        "full_name": user["full_name"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"]
    }

# Эндпоинты для карт
@app.get("/api/v1/cards", response_model=List[CardResponse])
async def get_user_cards(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
):
    """Получение карт пользователя"""
    try:
        # Получаем ID пользователя (заглушка)
        user = await db.fetch_one(
            "SELECT id FROM users WHERE email = $1",
            "nzosim@sfedu.ru"
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        cards = await db.fetch_all(
            "SELECT * FROM cards WHERE user_id = $1 AND is_active = true ORDER BY is_primary DESC",
            user["id"]
        )
        
        return [
            CardResponse(
                id=card["id"],
                masked_number=card["masked_number"],
                bank_name=card["bank_name"],
                card_type=card["card_type"],
                is_primary=card["is_primary"],
                expires_at=card["expires_at"],
                is_active=card["is_active"]
            )
            for card in cards
        ]
        
    except Exception as e:
        logger.error(f"Ошибка получения карт: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/api/v1/cards", response_model=CardResponse)
async def add_user_card(
    card_data: CardCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
):
    """Добавление новой карты"""
    try:
        # Получаем ID пользователя (заглушка)
        user = await db.fetch_one(
            "SELECT id FROM users WHERE email = $1",
            "nzosim@sfedu.ru"
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Если это первая карта или установлена как основная
        if card_data.is_primary:
            await db.execute(
                "UPDATE cards SET is_primary = false WHERE user_id = $1",
                user["id"]
            )
        
        card_id = await db.fetch_val(
            """
            INSERT INTO cards (user_id, masked_number, bank_name, card_type, is_primary, expires_at, token)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
            """,
            user["id"],
            card_data.masked_number,
            card_data.bank_name,
            card_data.card_type,
            card_data.is_primary,
            card_data.expires_at,
            f"token_{card_id}"
        )
        
        return CardResponse(
            id=card_id,
            masked_number=card_data.masked_number,
            bank_name=card_data.bank_name,
            card_type=card_data.card_type,
            is_primary=card_data.is_primary,
            expires_at=card_data.expires_at,
            is_active=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка добавления карты: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Эндпоинты для терминалов
@app.get("/api/v1/terminals", response_model=List[TerminalResponse])
async def get_terminals(
    status: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Получение списка терминалов"""
    try:
        query = "SELECT * FROM terminals WHERE is_active = true"
        params = []
        
        if status:
            query += " AND status = $1"
            params.append(status)
        
        query += " ORDER BY name"
        
        terminals = await db.fetch_all(query, *params)
        
        return [
            TerminalResponse(
                id=terminal["id"],
                serial_number=terminal["serial_number"],
                name=terminal["name"],
                location=terminal["location"],
                address=terminal["address"],
                status=terminal["status"],
                model=terminal["model"],
                manufacturer=terminal["manufacturer"],
                last_ping=terminal["last_ping"]
            )
            for terminal in terminals
        ]
        
    except Exception as e:
        logger.error(f"Ошибка получения терминалов: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/api/v1/terminals/{terminal_id}")
async def get_terminal(
    terminal_id: int,
    db: Database = Depends(get_db)
):
    """Получение информации о терминале"""
    try:
        terminal = await db.fetch_one(
            "SELECT * FROM terminals WHERE id = $1",
            terminal_id
        )
        
        if not terminal:
            raise HTTPException(status_code=404, detail="Терминал не найден")
        
        # Получаем статистику
        stats = await db.fetch_one(
            """
            SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(amount), 0) as total_amount,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_transactions
            FROM transactions 
            WHERE terminal_id = $1
            """,
            terminal_id
        )
        
        return {
            "id": terminal["id"],
            "serial_number": terminal["serial_number"],
            "name": terminal["name"],
            "location": terminal["location"],
            "address": terminal["address"],
            "status": terminal["status"],
            "model": terminal["model"],
            "manufacturer": terminal["manufacturer"],
            "last_ping": terminal["last_ping"],
            "statistics": {
                "total_transactions": stats["total_transactions"],
                "total_amount": float(stats["total_amount"]),
                "successful_transactions": stats["successful_transactions"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения терминала: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Эндпоинты для транзакций
@app.get("/api/v1/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
):
    """Получение списка транзакций"""
    try:
        # Получаем ID пользователя (заглушка)
        user = await db.fetch_one(
            "SELECT id FROM users WHERE email = $1",
            "nzosim@sfedu.ru"
        )
        
        query = """
        SELECT t.*, c.masked_number, c.bank_name, term.name as terminal_name
        FROM transactions t
        LEFT JOIN cards c ON t.card_id = c.id
        LEFT JOIN terminals term ON t.terminal_id = term.id
        WHERE t.user_id = $1
        """
        params = [user["id"]]
        
        if status:
            query += " AND t.status = $2"
            params.append(status)
        
        query += " ORDER BY t.created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
        params.extend([limit, offset])
        
        transactions = await db.fetch_all(query, *params)
        
        return [
            TransactionResponse(
                id=tx["id"],
                amount=float(tx["amount"]),
                currency=tx["currency"],
                status=tx["status"],
                payment_method=tx["payment_method"],
                description=tx["description"],
                created_at=tx["created_at"],
                completed_at=tx["completed_at"],
                card_info={
                    "masked_number": tx["masked_number"],
                    "bank_name": tx["bank_name"]
                },
                terminal_info={
                    "name": tx["terminal_name"]
                }
            )
            for tx in transactions
        ]
        
    except Exception as e:
        logger.error(f"Ошибка получения транзакций: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Эндпоинты для статистики
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db)
):
    """Получение статистики для дашборда"""
    try:
        # Общая статистика
        total_stats = await db.fetch_one(
            """
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT t.id) as total_terminals,
                COUNT(DISTINCT tr.id) as total_transactions,
                COALESCE(SUM(tr.amount), 0) as total_amount
            FROM users u
            CROSS JOIN terminals t
            CROSS JOIN transactions tr
            """
        )
        
        # Статистика за последние 30 дней
        recent_stats = await db.fetch_one(
            """
            SELECT 
                COUNT(*) as recent_transactions,
                COALESCE(SUM(amount), 0) as recent_amount
            FROM transactions
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            """
        )
        
        # Статус терминалов
        terminal_status = await db.fetch_all(
            """
            SELECT status, COUNT(*) as count
            FROM terminals
            WHERE is_active = true
            GROUP BY status
            """
        )
        
        return {
            "total_users": total_stats["total_users"],
            "total_terminals": total_stats["total_terminals"],
            "total_transactions": total_stats["total_transactions"],
            "total_amount": float(total_stats["total_amount"]),
            "recent_transactions": recent_stats["recent_transactions"],
            "recent_amount": float(recent_stats["recent_amount"]),
            "terminal_status": {
                status["status"]: status["count"]
                for status in terminal_status
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Эндпоинт для курсов валют
@app.get("/api/v1/currency/rates")
async def get_currency_rates():
    """Получение курсов валют"""
    # В реальности здесь будет запрос к внешнему API
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 