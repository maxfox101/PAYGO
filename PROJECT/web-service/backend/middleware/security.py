import time
import hashlib
import json
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from pydantic import BaseModel, ValidationError
import re

logger = logging.getLogger(__name__)

class SecurityConfig(BaseModel):
    # CORS настройки
    allowed_origins: List[str] = ["http://localhost:3000", "https://paygo.ru"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True
    
    # Rate limiting
    rate_limit_requests: int = 100  # запросов в минуту
    rate_limit_window: int = 60     # секунд
    burst_limit: int = 20           # максимальный burst
    
    # Security headers
    enable_hsts: bool = True
    hsts_max_age: int = 31536000    # 1 год
    enable_csp: bool = True
    enable_x_frame_options: bool = True
    enable_x_content_type_options: bool = True
    enable_referrer_policy: bool = True
    
    # Input validation
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    block_suspicious_patterns: bool = True
    max_nested_depth: int = 10
    
    # Session management
    session_timeout: int = 3600     # 1 час
    max_failed_attempts: int = 5
    lockout_duration: int = 900     # 15 минут

class RateLimiter:
    def __init__(self, redis_client: redis.Redis, config: SecurityConfig):
        self.redis = redis_client
        self.config = config
    
    async def is_allowed(self, key: str) -> bool:
        """Проверка rate limit для ключа"""
        try:
            current_time = int(time.time())
            window_start = current_time - self.config.rate_limit_window
            
            # Получаем текущие запросы
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.zcard(key)
            pipe.expire(key, self.config.rate_limit_window)
            results = await pipe.execute()
            
            current_requests = results[2]
            
            # Проверяем burst limit
            if current_requests > self.config.burst_limit:
                return False
            
            # Проверяем rate limit
            if current_requests > self.config.rate_limit_requests:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка rate limiter: {e}")
            return True  # В случае ошибки разрешаем запрос
    
    async def get_remaining_requests(self, key: str) -> int:
        """Получение оставшихся запросов"""
        try:
            current_time = int(time.time())
            window_start = current_time - self.config.rate_limit_window
            
            await self.redis.zremrangebyscore(key, 0, window_start)
            current_requests = await self.redis.zcard(key)
            
            return max(0, self.config.rate_limit_requests - current_requests)
            
        except Exception as e:
            logger.error(f"Ошибка получения оставшихся запросов: {e}")
            return 0

class InputValidator:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.suspicious_patterns = [
            r"<script[^>]*>.*?</script>",  # XSS
            r"javascript:",                 # JavaScript injection
            r"vbscript:",                  # VBScript injection
            r"on\w+\s*=",                  # Event handlers
            r"union\s+select",             # SQL injection
            r"drop\s+table",               # SQL injection
            r"exec\s*\(",                  # SQL injection
            r"eval\s*\(",                  # Code injection
            r"document\.",                 # DOM manipulation
            r"window\.",                   # Window object access
        ]
    
    def validate_input(self, data: str) -> bool:
        """Валидация входных данных"""
        if not self.config.block_suspicious_patterns:
            return True
        
        # Проверяем размер
        if len(data) > self.config.max_request_size:
            return False
        
        # Проверяем подозрительные паттерны
        for pattern in self.suspicious_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                logger.warning(f"Обнаружен подозрительный паттерн: {pattern}")
                return False
        
        # Проверяем глубину вложенности JSON
        try:
            parsed = json.loads(data) if isinstance(data, str) else data
            if self._get_nested_depth(parsed) > self.config.max_nested_depth:
                return False
        except:
            pass
        
        return True
    
    def _get_nested_depth(self, obj, current_depth=0) -> int:
        """Получение глубины вложенности объекта"""
        if current_depth > self.config.max_nested_depth:
            return current_depth
        
        if isinstance(obj, dict):
            return max(self._get_nested_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            return max(self._get_nested_depth(item, current_depth + 1) for item in obj)
        
        return current_depth

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: SecurityConfig, redis_client: redis.Redis):
        super().__init__(app)
        self.config = config
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client, config)
        self.input_validator = InputValidator(config)
        
        # Кэш заблокированных IP
        self.blocked_ips: Dict[str, Dict] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            # Получаем IP адрес
            client_ip = self._get_client_ip(request)
            
            # Проверяем блокировку IP
            if await self._is_ip_blocked(client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "IP заблокирован за подозрительную активность"}
                )
            
            # Rate limiting
            if not await self._check_rate_limit(request, client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Превышен лимит запросов"}
                )
            
            # Валидация входных данных
            if not await self._validate_request(request):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Недопустимые входные данные"}
                )
            
            # Выполняем запрос
            response = await call_next(request)
            
            # Добавляем security headers
            self._add_security_headers(response)
            
            # Логируем запрос
            await self._log_request(request, response, start_time, client_ip)
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка в security middleware: {e}")
            # В случае ошибки возвращаем 500, но не раскрываем детали
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Внутренняя ошибка сервера"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение реального IP адреса клиента"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _is_ip_blocked(self, client_ip: str) -> bool:
        """Проверка блокировки IP"""
        if client_ip in self.blocked_ips:
            block_info = self.blocked_ips[client_ip]
            if datetime.now() < block_info["until"]:
                return True
            else:
                del self.blocked_ips[client_ip]
        return False
    
    async def _check_rate_limit(self, request: Request, client_ip: str) -> bool:
        """Проверка rate limit"""
        # Создаем ключ для rate limiting
        rate_limit_key = f"rate_limit:{client_ip}:{request.url.path}"
        
        # Проверяем лимит
        if not await self.rate_limiter.is_allowed(rate_limit_key):
            # Увеличиваем счетчик неудачных попыток
            await self._increment_failed_attempts(client_ip)
            return False
        
        return True
    
    async def _increment_failed_attempts(self, client_ip: str):
        """Увеличение счетчика неудачных попыток"""
        try:
            failed_key = f"failed_attempts:{client_ip}"
            failed_count = await self.redis.incr(failed_key)
            await self.redis.expire(failed_key, self.config.lockout_duration)
            
            # Если превышен лимит - блокируем IP
            if failed_count >= self.config.max_failed_attempts:
                block_until = datetime.now() + timedelta(seconds=self.config.lockout_duration)
                self.blocked_ips[client_ip] = {
                    "until": block_until,
                    "reason": "rate_limit_exceeded"
                }
                logger.warning(f"IP {client_ip} заблокирован за превышение rate limit")
                
        except Exception as e:
            logger.error(f"Ошибка при блокировке IP: {e}")
    
    async def _validate_request(self, request: Request) -> bool:
        """Валидация запроса"""
        try:
            # Проверяем размер запроса
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.config.max_request_size:
                return False
            
            # Валидируем тело запроса для POST/PUT/PATCH
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                if body:
                    # Пытаемся декодировать как JSON
                    try:
                        body_str = body.decode('utf-8')
                        if not self.input_validator.validate_input(body_str):
                            return False
                    except:
                        # Если не JSON, проверяем как строку
                        if not self.input_validator.validate_input(body.decode('utf-8', errors='ignore')):
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации запроса: {e}")
            return False
    
    def _add_security_headers(self, response: Response):
        """Добавление security headers"""
        # HSTS
        if self.config.enable_hsts:
            response.headers["Strict-Transport-Security"] = f"max-age={self.config.hsts_max_age}; includeSubDomains"
        
        # Content Security Policy
        if self.config.enable_csp:
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
            response.headers["Content-Security-Policy"] = csp_policy
        
        # X-Frame-Options
        if self.config.enable_x_frame_options:
            response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        if self.config.enable_x_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer Policy
        if self.config.enable_referrer_policy:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
    
    async def _log_request(self, request: Request, response: Response, start_time: float, client_ip: str):
        """Логирование запроса"""
        duration = time.time() - start_time
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "duration": round(duration, 3),
            "content_length": response.headers.get("content-length", 0)
        }
        
        # Логируем в зависимости от статуса
        if response.status_code >= 400:
            logger.warning(f"Запрос с ошибкой: {log_data}")
        elif duration > 1.0:  # Медленные запросы
            logger.info(f"Медленный запрос: {log_data}")
        else:
            logger.debug(f"Запрос: {log_data}")

# Глобальная конфигурация безопасности
security_config = SecurityConfig()

# Функция для создания middleware
def create_security_middleware(redis_client: redis.Redis) -> SecurityMiddleware:
    return SecurityMiddleware(None, security_config, redis_client)

