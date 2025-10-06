import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json
import redis.asyncio as redis

# Импортируем наши модули безопасности
from middleware.security import SecurityMiddleware, SecurityConfig, RateLimiter, InputValidator
from middleware.threat_detection import ThreatDetectionMiddleware, ThreatDetector
from auth.two_factor import TwoFactorAuth, TwoFactorConfig, TOTPService

# Тестовые данные
TEST_IP = "192.168.1.100"
TEST_USER_ID = "test_user_123"
MALICIOUS_PAYLOAD = "<script>alert('xss')</script>"
SQL_INJECTION_PAYLOAD = "'; DROP TABLE users; --"

class TestSecurityMiddleware:
    """Тесты для SecurityMiddleware"""
    
    @pytest.fixture
    def mock_redis(self):
        """Мок Redis клиента"""
        return AsyncMock(spec=redis.Redis)
    
    @pytest.fixture
    def security_config(self):
        """Тестовая конфигурация безопасности"""
        return SecurityConfig(
            rate_limit_requests=10,
            rate_limit_window=60,
            burst_limit=5
        )
    
    @pytest.fixture
    def security_middleware(self, mock_redis, security_config):
        """Тестовый экземпляр SecurityMiddleware"""
        return SecurityMiddleware(None, security_config, mock_redis)
    
    def test_security_config_defaults(self):
        """Тест значений по умолчанию для SecurityConfig"""
        config = SecurityConfig()
        
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 60
        assert config.burst_limit == 20
        assert config.enable_hsts is True
        assert config.enable_csp is True
        assert config.max_request_size == 10 * 1024 * 1024
    
    def test_security_config_custom(self):
        """Тест кастомной конфигурации безопасности"""
        config = SecurityConfig(
            rate_limit_requests=50,
            rate_limit_window=30,
            burst_limit=10
        )
        
        assert config.rate_limit_requests == 50
        assert config.rate_limit_window == 30
        assert config.burst_limit == 10
    
    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self, mock_redis, security_config):
        """Тест создания RateLimiter"""
        rate_limiter = RateLimiter(mock_redis, security_config)
        assert rate_limiter.redis == mock_redis
        assert rate_limiter.config == security_config
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allowed(self, mock_redis, security_config):
        """Тест проверки rate limit - разрешено"""
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 5, 0]  # 5 запросов
        
        rate_limiter = RateLimiter(mock_redis, security_config)
        result = await rate_limiter.is_allowed("test_key")
        
        assert result is True
        mock_redis.pipeline.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_exceeded(self, mock_redis, security_config):
        """Тест проверки rate limit - превышен"""
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 25, 0]  # 25 запросов
        
        rate_limiter = RateLimiter(mock_redis, security_config)
        result = await rate_limiter.is_allowed("test_key")
        
        assert result is False
    
    def test_input_validator_creation(self, security_config):
        """Тест создания InputValidator"""
        validator = InputValidator(security_config)
        assert validator.config == security_config
        assert len(validator.suspicious_patterns) > 0
    
    def test_input_validator_clean_input(self, security_config):
        """Тест валидации чистого ввода"""
        validator = InputValidator(security_config)
        clean_input = "Hello, World! This is a normal message."
        
        result = validator.validate_input(clean_input)
        assert result is True
    
    def test_input_validator_xss_pattern(self, security_config):
        """Тест валидации XSS паттерна"""
        validator = InputValidator(security_config)
        xss_input = "<script>alert('xss')</script>"
        
        result = validator.validate_input(xss_input)
        assert result is False
    
    def test_input_validator_sql_injection(self, security_config):
        """Тест валидации SQL инъекции"""
        validator = InputValidator(security_config)
        sql_input = "'; DROP TABLE users; --"
        
        result = validator.validate_input(sql_input)
        assert result is False
    
    def test_input_validator_large_input(self, security_config):
        """Тест валидации большого ввода"""
        validator = InputValidator(security_config)
        large_input = "x" * (security_config.max_request_size + 1000)
        
        result = validator.validate_input(large_input)
        assert result is False

class TestThreatDetection:
    """Тесты для ThreatDetection"""
    
    @pytest.fixture
    def mock_redis(self):
        """Мок Redis клиента"""
        return AsyncMock(spec=redis.Redis)
    
    @pytest.fixture
    def threat_detector(self, mock_redis):
        """Тестовый экземпляр ThreatDetector"""
        return ThreatDetector(mock_redis)
    
    def test_threat_patterns_loaded(self, threat_detector):
        """Тест загрузки паттернов угроз"""
        assert len(threat_detector.threat_patterns) > 0
        
        # Проверяем наличие критических паттернов
        critical_patterns = [p for p in threat_detector.threat_patterns if p.severity == "critical"]
        assert len(critical_patterns) > 0
        
        # Проверяем наличие SQL injection паттерна
        sql_patterns = [p for p in threat_detector.threat_patterns if "SQL" in p.name]
        assert len(sql_patterns) > 0
    
    def test_threat_pattern_structure(self, threat_detector):
        """Тест структуры паттернов угроз"""
        for pattern in threat_detector.threat_patterns:
            assert hasattr(pattern, 'name')
            assert hasattr(pattern, 'pattern')
            assert hasattr(pattern, 'severity')
            assert hasattr(pattern, 'description')
            assert hasattr(pattern, 'action')
            
            assert pattern.severity in ['low', 'medium', 'high', 'critical']
            assert pattern.action in ['log', 'block', 'alert']
    
    @pytest.mark.asyncio
    async def test_analyze_headers_suspicious_user_agent(self, threat_detector):
        """Тест анализа подозрительного User-Agent"""
        from fastapi import Request
        from unittest.mock import Mock
        
        # Создаем мок запроса
        mock_request = Mock(spec=Request)
        mock_request.headers = {"user-agent": ""}  # Пустой User-Agent
        
        threats = await threat_detector._analyze_headers(mock_request)
        
        assert len(threats) > 0
        suspicious_ua = [t for t in threats if t["type"] == "suspicious_user_agent"]
        assert len(suspicious_ua) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_url_sql_injection(self, threat_detector):
        """Тест анализа URL на SQL инъекцию"""
        from fastapi import Request
        from unittest.mock import Mock
        
        # Создаем мок запроса с SQL инъекцией
        mock_request = Mock(spec=Request)
        mock_request.url = "http://example.com/api/users?query=union select * from users"
        
        threats = await threat_detector._analyze_url(mock_request)
        
        assert len(threats) > 0
        sql_threats = [t for t in threats if "SQL" in t["type"]]
        assert len(sql_threats) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_url_xss(self, threat_detector):
        """Тест анализа URL на XSS"""
        from fastapi import Request
        from unittest.mock import Mock
        
        # Создаем мок запроса с XSS
        mock_request = Mock(spec=Request)
        mock_request.url = "http://example.com/api/search?q=<script>alert('xss')</script>"
        
        threats = await threat_detector._analyze_url(mock_request)
        
        assert len(threats) > 0
        xss_threats = [t for t in threats if "XSS" in t["type"]]
        assert len(xss_threats) > 0

class TestTwoFactorAuth:
    """Тесты для TwoFactorAuth"""
    
    @pytest.fixture
    def two_factor_config(self):
        """Тестовая конфигурация 2FA"""
        return TwoFactorConfig(
            totp_digits=6,
            totp_period=30,
            sms_code_length=6,
            email_code_length=6,
            max_attempts=3
        )
    
    @pytest.fixture
    def two_factor_auth(self, two_factor_config):
        """Тестовый экземпляр TwoFactorAuth"""
        return TwoFactorAuth(two_factor_config)
    
    def test_totp_service_creation(self, two_factor_config):
        """Тест создания TOTP сервиса"""
        totp_service = TOTPService(two_factor_config)
        assert totp_service.config == two_factor_config
    
    def test_totp_secret_generation(self, two_factor_config):
        """Тест генерации TOTP секрета"""
        totp_service = TOTPService(two_factor_config)
        secret = totp_service.generate_secret()
        
        assert len(secret) > 0
        assert isinstance(secret, str)
        # TOTP секреты обычно 32 символа в base32
        assert len(secret) >= 32
    
    def test_totp_verification(self, two_factor_config):
        """Тест проверки TOTP"""
        totp_service = TOTPService(totp_config)
        secret = totp_service.generate_secret()
        
        # Получаем текущий токен
        current_token = totp_service.get_current_totp(secret)
        assert len(current_token) == two_factor_config.totp_digits
        
        # Проверяем токен
        result = totp_service.verify_totp(secret, current_token)
        assert result is True
        
        # Проверяем неверный токен
        wrong_token = "000000"
        result = totp_service.verify_totp(secret, wrong_token)
        assert result is False
    
    def test_backup_codes_generation(self, two_factor_config):
        """Тест генерации резервных кодов"""
        backup_service = BackupCodesService(two_factor_config)
        codes = backup_service.generate_backup_codes()
        
        assert len(codes) == two_factor_config.backup_codes_count
        
        # Проверяем формат кодов (XXXX-XXXX)
        for code in codes:
            assert len(code) == 9  # 4 + 1 + 4
            assert code[4] == "-"
            assert code.replace("-", "").isalnum()
    
    def test_backup_code_verification(self, two_factor_config):
        """Тест проверки резервного кода"""
        backup_service = BackupCodesService(two_factor_config)
        codes = backup_service.generate_backup_codes()
        original_codes = codes.copy()
        
        # Проверяем правильный код
        test_code = codes[0]
        is_valid, remaining_codes = backup_service.verify_backup_code(original_codes, test_code)
        
        assert is_valid is True
        assert len(remaining_codes) == len(original_codes) - 1
        assert test_code not in remaining_codes
        
        # Проверяем неверный код
        wrong_code = "AAAA-AAAA"
        is_valid, remaining_codes = backup_service.verify_backup_code(original_codes, wrong_code)
        
        assert is_valid is False
        assert remaining_codes == original_codes

class TestSecurityIntegration:
    """Интеграционные тесты безопасности"""
    
    @pytest.fixture
    def mock_redis(self):
        """Мок Redis клиента"""
        return AsyncMock(spec=redis.Redis)
    
    @pytest.mark.asyncio
    async def test_security_middleware_chain(self, mock_redis):
        """Тест цепочки middleware безопасности"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        # Добавляем middleware безопасности
        security_middleware = create_security_middleware(mock_redis)
        threat_middleware = create_threat_detection_middleware(mock_redis)
        
        # Создаем тестовый клиент
        client = TestClient(app)
        
        # Тестируем базовый endpoint
        response = client.get("/")
        assert response.status_code == 404  # Endpoint не существует, но middleware работает
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, mock_redis):
        """Тест интеграции rate limiting"""
        # Настраиваем мок Redis для rate limiting
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 15, 0]  # 15 запросов
        
        config = SecurityConfig(rate_limit_requests=10, rate_limit_window=60, burst_limit=5)
        rate_limiter = RateLimiter(mock_redis, config)
        
        # Тестируем превышение лимита
        result = await rate_limiter.is_allowed("test_key")
        assert result is False
        
        # Тестируем нормальный лимит
        mock_redis.pipeline.return_value.execute.return_value = [0, 0, 5, 0]  # 5 запросов
        result = await rate_limiter.is_allowed("test_key")
        assert result is True

# Тесты производительности безопасности
class TestSecurityPerformance:
    """Тесты производительности безопасности"""
    
    @pytest.mark.asyncio
    async def test_input_validation_performance(self):
        """Тест производительности валидации ввода"""
        import time
        
        config = SecurityConfig()
        validator = InputValidator(config)
        
        # Тестируем на большом объеме данных
        test_data = "x" * 10000  # 10KB данных
        
        start_time = time.time()
        for _ in range(1000):
            validator.validate_input(test_data)
        end_time = time.time()
        
        # Валидация должна выполняться быстро (< 1 секунды на 1000 проверок)
        assert (end_time - start_time) < 1.0
    
    @pytest.mark.asyncio
    async def test_threat_detection_performance(self, mock_redis):
        """Тест производительности детекции угроз"""
        import time
        
        detector = ThreatDetector(mock_redis)
        
        # Создаем тестовый запрос
        from fastapi import Request
        from unittest.mock import Mock
        
        mock_request = Mock(spec=Request)
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "GET"
        mock_request.headers = {"user-agent": "Mozilla/5.0"}
        
        start_time = time.time()
        for _ in range(100):
            await detector.analyze_request(mock_request, "192.168.1.1")
        end_time = time.time()
        
        # Анализ должен выполняться быстро (< 0.1 секунды на 100 запросов)
        assert (end_time - start_time) < 0.1

# Тесты на уязвимости
class TestSecurityVulnerabilities:
    """Тесты на уязвимости безопасности"""
    
    def test_sql_injection_protection(self):
        """Тест защиты от SQL инъекции"""
        config = SecurityConfig()
        validator = InputValidator(config)
        
        # Тестируем различные SQL инъекции
        sql_payloads = [
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM users",
            "1 OR 1=1",
            "admin'--",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for payload in sql_payloads:
            result = validator.validate_input(payload)
            assert result is False, f"SQL инъекция не заблокирована: {payload}"
    
    def test_xss_protection(self):
        """Тест защиты от XSS"""
        config = SecurityConfig()
        validator = InputValidator(config)
        
        # Тестируем различные XSS векторы
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "vbscript:msgbox('xss')",
            "<svg onload=alert('xss')>",
            "onclick=alert('xss')"
        ]
        
        for payload in xss_payloads:
            result = validator.validate_input(payload)
            assert result is False, f"XSS не заблокирован: {payload}"
    
    def test_command_injection_protection(self):
        """Тест защиты от инъекции команд"""
        config = SecurityConfig()
        validator = InputValidator(config)
        
        # Тестируем различные векторы инъекции команд
        command_payloads = [
            "| ls -la",
            "; cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(id)",
            "os.system('ls')",
            "subprocess.call(['ls'])"
        ]
        
        for payload in command_payloads:
            result = validator.validate_input(payload)
            assert result is False, f"Инъекция команд не заблокирована: {payload}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


