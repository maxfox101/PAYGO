import pytest
import asyncio
import os
import tempfile
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import redis.asyncio as redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Импортируем наши модули
from main import app
from database import get_db, Base
from config import get_settings

# Тестовая конфигурация
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_REDIS_URL = "redis://localhost:6379/1"

@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_settings():
    """Тестовые настройки"""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.redis_url = TEST_REDIS_URL
    settings.secret_key = "test_secret_key_12345"
    settings.debug = True
    return settings

@pytest.fixture(scope="session")
def test_engine():
    """Тестовый движок базы данных"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Фабрика тестовых сессий"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    return TestingSessionLocal

@pytest.fixture(scope="function")
def test_db(test_engine, test_session_factory):
    """Тестовая база данных"""
    # Создаем таблицы
    Base.metadata.create_all(bind=test_engine)
    
    # Создаем сессию
    session = test_session_factory()
    
    yield session
    
    # Очищаем после теста
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def mock_redis():
    """Мок Redis клиента"""
    mock_redis = AsyncMock(spec=redis.Redis)
    
    # Настраиваем базовые методы
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = 0
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    mock_redis.pipeline.return_value.execute.return_value = [0, 0, 0, 0]
    
    return mock_redis

@pytest.fixture(scope="function")
def test_client(test_db, mock_redis):
    """Тестовый клиент FastAPI"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    def override_get_redis():
        return mock_redis
    
    # Подменяем зависимости
    app.dependency_overrides[get_db] = override_get_db
    # app.dependency_overrides[get_redis] = override_get_redis
    
    with TestClient(app) as client:
        yield client
    
    # Очищаем подмены
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_user_data():
    """Тестовые данные пользователя"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Тест",
        "last_name": "Пользователь",
        "phone": "+79001234567",
        "role": "user"
    }

@pytest.fixture(scope="function")
def sample_card_data():
    """Тестовые данные карты"""
    return {
        "card_number": "4111111111111111",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvv": "123",
        "cardholder_name": "TEST USER"
    }

@pytest.fixture(scope="function")
def sample_transaction_data():
    """Тестовые данные транзакции"""
    return {
        "amount": 1000.00,
        "currency": "RUB",
        "description": "Тестовая транзакция",
        "merchant_id": "test_merchant_123"
    }

@pytest.fixture(scope="function")
def admin_user_data():
    """Тестовые данные администратора"""
    return {
        "email": "admin@paygo.ru",
        "password": "adminpass123",
        "first_name": "Админ",
        "last_name": "Системы",
        "phone": "+79001234568",
        "role": "admin",
        "permissions": ["manage_users", "manage_terminals", "view_audit_logs"]
    }

@pytest.fixture(scope="function")
def terminal_operator_data():
    """Тестовые данные оператора терминала"""
    return {
        "email": "operator@paygo.ru",
        "password": "operatorpass123",
        "first_name": "Оператор",
        "last_name": "Терминала",
        "phone": "+79001234569",
        "role": "terminal_operator",
        "permissions": ["manage_terminals", "process_transactions"]
    }

@pytest.fixture(scope="function")
def temp_file():
    """Временный файл для тестов"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test file content")
        temp_path = f.name
    
    yield temp_path
    
    # Удаляем временный файл
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture(scope="function")
def mock_payment_processor():
    """Мок платежного процессора"""
    mock = MagicMock()
    mock.process_payment.return_value = {
        "success": True,
        "transaction_id": "test_txn_123",
        "status": "completed",
        "amount": 1000.00
    }
    mock.refund_payment.return_value = {
        "success": True,
        "refund_id": "test_refund_123",
        "status": "completed"
    }
    return mock

@pytest.fixture(scope="function")
def mock_notification_service():
    """Мок сервиса уведомлений"""
    mock = MagicMock()
    mock.send_notification.return_value = True
    mock.send_bulk_notifications.return_value = [True, True, True]
    return mock

@pytest.fixture(scope="function")
def mock_backup_manager():
    """Мок менеджера резервных копий"""
    mock = MagicMock()
    mock.create_database_backup.return_value = "backup_20231201_120000.sql"
    mock.cleanup_old_backups.return_value = 2
    return mock

@pytest.fixture(scope="function")
def mock_audit_logger():
    """Мок аудит логгера"""
    mock = MagicMock()
    mock.log_event.return_value = True
    mock.log_user_action.return_value = True
    return mock

@pytest.fixture(scope="function")
def mock_two_factor_auth():
    """Мок двухфакторной аутентификации"""
    mock = MagicMock()
    mock.setup_totp.return_value = {
        "secret": "test_secret_123",
        "qr_code": "data:image/png;base64,test_qr_code",
        "backup_codes": ["AAAA-AAAA", "BBBB-BBBB"]
    }
    mock.verify_totp.return_value = True
    mock.send_sms_code.return_value = True
    mock.send_email_code.return_value = True
    return mock

# Фикстуры для тестирования производительности
@pytest.fixture(scope="function")
def large_dataset():
    """Большой набор данных для тестирования производительности"""
    return {
        "users": [{"email": f"user{i}@test.com", "name": f"User {i}"} for i in range(1000)],
        "transactions": [{"amount": i * 10.0, "id": f"txn_{i}"} for i in range(1000)],
        "cards": [{"number": f"4111{i:012d}", "id": f"card_{i}"} for i in range(1000)]
    }

@pytest.fixture(scope="function")
def performance_timer():
    """Таймер для тестов производительности"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
    
    return Timer()

# Фикстуры для тестирования безопасности
@pytest.fixture(scope="function")
def malicious_payloads():
    """Вредоносные payloads для тестирования безопасности"""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM users",
            "1 OR 1=1",
            "admin'--",
            "'; EXEC xp_cmdshell('dir'); --"
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "vbscript:msgbox('xss')",
            "<svg onload=alert('xss')>"
        ],
        "command_injection": [
            "| ls -la",
            "; cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(id)"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    }

@pytest.fixture(scope="function")
def rate_limit_scenarios():
    """Сценарии для тестирования rate limiting"""
    return {
        "normal_user": {"requests_per_minute": 50, "burst_limit": 10},
        "power_user": {"requests_per_minute": 200, "burst_limit": 50},
        "api_client": {"requests_per_minute": 1000, "burst_limit": 100},
        "suspicious": {"requests_per_minute": 1000, "burst_limit": 1000}
    }

# Фикстуры для интеграционных тестов
@pytest.fixture(scope="function")
def test_app_with_middleware(test_db, mock_redis):
    """Тестовое приложение с middleware"""
    from fastapi import FastAPI
    from middleware.security import create_security_middleware
    from middleware.threat_detection import create_threat_detection_middleware
    
    test_app = FastAPI()
    
    # Добавляем тестовые endpoints
    @test_app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @test_app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    # Добавляем middleware
    test_app.add_middleware(create_security_middleware(mock_redis))
    test_app.add_middleware(create_threat_detection_middleware(mock_redis))
    
    return test_app

@pytest.fixture(scope="function")
def integration_client(test_app_with_middleware):
    """Клиент для интеграционных тестов"""
    return TestClient(test_app_with_middleware)

# Настройки pytest
def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов"""
    for item in items:
        # Автоматически помечаем тесты по имени файла
        if "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


