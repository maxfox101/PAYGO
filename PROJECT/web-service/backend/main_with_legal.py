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

# Подключение роутеров
app.include_router(legal_documents_router, prefix="/api/v1/legal", tags=["Правовые документы"])

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
            "Веб-интерфейс управления",
            "Правовые документы"
        ]
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
        "main_with_legal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
