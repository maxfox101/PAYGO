import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from pydantic import BaseModel
import re
import ipaddress
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ThreatPattern(BaseModel):
    name: str
    pattern: str
    severity: str  # low, medium, high, critical
    description: str
    action: str    # log, block, alert

class AnomalyThreshold(BaseModel):
    requests_per_minute: int = 100
    failed_auth_per_minute: int = 5
    suspicious_patterns_per_minute: int = 10
    large_requests_per_minute: int = 5
    unusual_user_agents: int = 3

class ThreatDetector:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Паттерны угроз
        self.threat_patterns = [
            ThreatPattern(
                name="SQL Injection",
                pattern=r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
                severity="high",
                description="Попытка SQL инъекции",
                action="block"
            ),
            ThreatPattern(
                name="XSS Attack",
                pattern=r"(<script|javascript:|vbscript:|on\w+\s*=)",
                severity="high",
                description="Попытка XSS атаки",
                action="block"
            ),
            ThreatPattern(
                name="Path Traversal",
                pattern=r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
                severity="medium",
                description="Попытка обхода директорий",
                action="log"
            ),
            ThreatPattern(
                name="Command Injection",
                pattern=r"(\b(cmd|command|exec|system|eval|os\.|subprocess)\b)",
                severity="critical",
                description="Попытка выполнения команд",
                action="block"
            ),
            ThreatPattern(
                name="File Upload Attack",
                pattern=r"\.(php|jsp|asp|aspx|exe|bat|cmd|sh|bash)$",
                severity="high",
                description="Попытка загрузки опасного файла",
                action="block"
            ),
            ThreatPattern(
                name="Brute Force",
                pattern=r"login|auth|signin",
                severity="medium",
                description="Подозрительная активность аутентификации",
                action="alert"
            )
        ]
        
        # Кэш для детекции аномалий
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.suspicious_ips: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        
        # Пороги для аномалий
        self.thresholds = AnomalyThreshold()
    
    async def analyze_request(self, request: Request, client_ip: str) -> Tuple[bool, str, Dict]:
        """Анализ запроса на предмет угроз"""
        try:
            # Проверяем блокировку IP
            if client_ip in self.blocked_ips:
                return False, "IP заблокирован", {"reason": "blocked_ip"}
            
            # Анализируем заголовки
            header_threats = await self._analyze_headers(request)
            if header_threats:
                return False, "Подозрительные заголовки", {"threats": header_threats}
            
            # Анализируем URL
            url_threats = await self._analyze_url(request)
            if url_threats:
                return False, "Подозрительный URL", {"threats": url_threats}
            
            # Анализируем тело запроса
            body_threats = await self._analyze_request_body(request)
            if body_threats:
                return False, "Подозрительное тело запроса", {"threats": body_threats}
            
            # Проверяем аномалии
            anomaly_detected = await self._detect_anomalies(request, client_ip)
            if anomaly_detected:
                return False, "Обнаружена аномалия", {"anomaly": anomaly_detected}
            
            # Обновляем историю запросов
            await self._update_request_history(request, client_ip)
            
            return True, "OK", {}
            
        except Exception as e:
            logger.error(f"Ошибка анализа запроса: {e}")
            return False, "Ошибка анализа", {"error": str(e)}
    
    async def _analyze_headers(self, request: Request) -> List[Dict]:
        """Анализ заголовков запроса"""
        threats = []
        
        # Проверяем User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or user_agent.lower() in ["", "null", "undefined"]:
            threats.append({
                "type": "suspicious_user_agent",
                "severity": "medium",
                "description": "Отсутствует или подозрительный User-Agent"
            })
        
        # Проверяем Referer
        referer = request.headers.get("referer", "")
        if referer and not self._is_valid_referer(referer, str(request.url)):
            threats.append({
                "type": "suspicious_referer",
                "severity": "medium",
                "description": "Подозрительный Referer заголовок"
            })
        
        # Проверяем Content-Type
        content_type = request.headers.get("content-type", "")
        if request.method in ["POST", "PUT", "PATCH"] and not content_type:
            threats.append({
                "type": "missing_content_type",
                "severity": "low",
                "description": "Отсутствует Content-Type для POST запроса"
            })
        
        return threats
    
    async def _analyze_url(self, request: Request) -> List[Dict]:
        """Анализ URL запроса"""
        threats = []
        url = str(request.url)
        
        # Проверяем на паттерны угроз
        for pattern in self.threat_patterns:
            if re.search(pattern.pattern, url, re.IGNORECASE):
                threats.append({
                    "type": pattern.name,
                    "severity": pattern.severity,
                    "description": pattern.description,
                    "action": pattern.action
                })
        
        # Проверяем длину URL
        if len(url) > 2048:
            threats.append({
                "type": "long_url",
                "severity": "medium",
                "description": "URL слишком длинный"
            })
        
        # Проверяем на подозрительные параметры
        if "?" in url:
            query_params = url.split("?")[1]
            if len(query_params) > 1000:
                threats.append({
                    "type": "long_query_params",
                    "severity": "low",
                    "description": "Слишком длинные параметры запроса"
                })
        
        return threats
    
    async def _analyze_request_body(self, request: Request) -> List[Dict]:
        """Анализ тела запроса"""
        threats = []
        
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Получаем тело запроса
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    
                    # Проверяем на паттерны угроз
                    for pattern in self.threat_patterns:
                        if re.search(pattern.pattern, body_str, re.IGNORECASE):
                            threats.append({
                                "type": pattern.name,
                                "severity": pattern.severity,
                                "description": pattern.description,
                                "action": pattern.action
                            })
                    
                    # Проверяем размер тела
                    if len(body) > 10 * 1024 * 1024:  # 10MB
                        threats.append({
                            "type": "large_request_body",
                            "severity": "medium",
                            "description": "Тело запроса слишком большое"
                        })
                    
                    # Проверяем на подозрительные MIME типы
                    content_type = request.headers.get("content-type", "")
                    if "multipart/form-data" in content_type:
                        if re.search(r"\.(php|jsp|asp|exe|bat|cmd|sh)$", body_str, re.IGNORECASE):
                            threats.append({
                                "type": "dangerous_file_upload",
                                "severity": "critical",
                                "description": "Попытка загрузки опасного файла"
                            })
                
            except Exception as e:
                logger.error(f"Ошибка анализа тела запроса: {e}")
                threats.append({
                    "type": "body_analysis_error",
                    "severity": "medium",
                    "description": "Ошибка анализа тела запроса"
                })
        
        return threats
    
    async def _detect_anomalies(self, request: Request, client_ip: str) -> Optional[Dict]:
        """Детекция аномалий"""
        try:
            current_time = datetime.now()
            window_start = current_time - timedelta(minutes=1)
            
            # Получаем статистику запросов для IP
            request_key = f"requests:{client_ip}"
            requests_data = await self.redis.get(request_key)
            
            if requests_data:
                requests = json.loads(requests_data)
                # Фильтруем запросы за последнюю минуту
                recent_requests = [req for req in requests if datetime.fromisoformat(req["timestamp"]) > window_start]
            else:
                recent_requests = []
            
            # Проверяем количество запросов в минуту
            if len(recent_requests) > self.thresholds.requests_per_minute:
                return {
                    "type": "high_request_rate",
                    "severity": "high",
                    "description": f"Превышен лимит запросов: {len(recent_requests)} в минуту"
                }
            
            # Проверяем количество неудачных аутентификаций
            failed_auth = [req for req in recent_requests if req.get("status_code") == 401]
            if len(failed_auth) > self.thresholds.failed_auth_per_minute:
                return {
                    "type": "brute_force_attempt",
                    "severity": "high",
                    "description": f"Много неудачных попыток входа: {len(failed_auth)}"
                }
            
            # Проверяем подозрительные паттерны
            suspicious_patterns = [req for req in recent_requests if req.get("suspicious", False)]
            if len(suspicious_patterns) > self.thresholds.suspicious_patterns_per_minute:
                return {
                    "type": "suspicious_patterns",
                    "severity": "medium",
                    "description": f"Много подозрительных паттернов: {len(suspicious_patterns)}"
                }
            
            # Проверяем большие запросы
            large_requests = [req for req in recent_requests if req.get("size", 0) > 1024 * 1024]  # >1MB
            if len(large_requests) > self.thresholds.large_requests_per_minute:
                return {
                    "type": "large_requests",
                    "severity": "medium",
                    "description": f"Много больших запросов: {len(large_requests)}"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка детекции аномалий: {e}")
            return None
    
    async def _update_request_history(self, request: Request, client_ip: str):
        """Обновление истории запросов"""
        try:
            request_key = f"requests:{client_ip}"
            
            # Получаем текущую историю
            requests_data = await self.redis.get(request_key)
            if requests_data:
                requests = json.loads(requests_data)
            else:
                requests = []
            
            # Добавляем новый запрос
            new_request = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "url": str(request.url),
                "status_code": 200,  # Будет обновлено позже
                "size": request.headers.get("content-length", 0),
                "suspicious": False,
                "user_agent": request.headers.get("user-agent", "")
            }
            
            requests.append(new_request)
            
            # Ограничиваем историю последними 1000 запросами
            if len(requests) > 1000:
                requests = requests[-1000:]
            
            # Сохраняем в Redis с TTL 1 час
            await self.redis.setex(request_key, 3600, json.dumps(requests))
            
        except Exception as e:
            logger.error(f"Ошибка обновления истории запросов: {e}")
    
    def _is_valid_referer(self, referer: str, current_url: str) -> bool:
        """Проверка валидности Referer"""
        try:
            # Извлекаем домен из referer
            if referer.startswith("http"):
                referer_domain = referer.split("/")[2]
            else:
                referer_domain = referer.split("/")[0]
            
            # Извлекаем домен из текущего URL
            if current_url.startswith("http"):
                current_domain = current_url.split("/")[2]
            else:
                current_domain = current_url.split("/")[0]
            
            # Проверяем, что referer с того же домена или с доверенных доменов
            trusted_domains = ["localhost", "127.0.0.1", "paygo.ru", "api.paygo.ru"]
            
            return (referer_domain == current_domain or 
                   referer_domain in trusted_domains or
                   referer_domain.endswith(".paygo.ru"))
            
        except Exception:
            return False
    
    async def block_ip(self, client_ip: str, reason: str, duration_minutes: int = 60):
        """Блокировка IP адреса"""
        try:
            self.blocked_ips.add(client_ip)
            
            # Сохраняем в Redis
            block_data = {
                "reason": reason,
                "blocked_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
            }
            
            await self.redis.setex(
                f"blocked_ip:{client_ip}",
                duration_minutes * 60,
                json.dumps(block_data)
            )
            
            logger.warning(f"IP {client_ip} заблокирован: {reason}")
            
        except Exception as e:
            logger.error(f"Ошибка блокировки IP {client_ip}: {e}")
    
    async def mark_suspicious(self, client_ip: str, reason: str):
        """Пометка IP как подозрительного"""
        try:
            self.suspicious_ips.add(client_ip)
            
            # Сохраняем в Redis
            suspicious_data = {
                "reason": reason,
                "marked_at": datetime.now().isoformat(),
                "count": 1
            }
            
            existing_data = await self.redis.get(f"suspicious_ip:{client_ip}")
            if existing_data:
                existing = json.loads(existing_data)
                suspicious_data["count"] = existing["count"] + 1
            
            await self.redis.setex(
                f"suspicious_ip:{client_ip}",
                3600,  # 1 час
                json.dumps(suspicious_data)
            )
            
            logger.info(f"IP {client_ip} помечен как подозрительный: {reason}")
            
        except Exception as e:
            logger.error(f"Ошибка пометки IP {client_ip} как подозрительного: {e}")

class ThreatDetectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.threat_detector = ThreatDetector(redis_client)
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Получаем IP адрес клиента
            client_ip = self._get_client_ip(request)
            
            # Анализируем запрос на угрозы
            is_safe, message, details = await self.threat_detector.analyze_request(request, client_ip)
            
            if not is_safe:
                # Логируем угрозу
                logger.warning(f"Обнаружена угроза от {client_ip}: {message} - {details}")
                
                # Помечаем IP как подозрительный
                await self.threat_detector.mark_suspicious(client_ip, message)
                
                # Блокируем IP если угроза критическая
                if any(threat.get("severity") == "critical" for threat in details.get("threats", [])):
                    await self.threat_detector.block_ip(client_ip, "critical_threat_detected")
                
                # Возвращаем ошибку
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Доступ запрещен",
                        "message": message,
                        "details": details
                    }
                )
            
            # Выполняем запрос
            response = await call_next(request)
            
            # Обновляем статус код в истории
            await self._update_response_status(request, client_ip, response.status_code)
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка в threat detection middleware: {e}")
            # В случае ошибки продолжаем выполнение
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Получение реального IP адреса клиента"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _update_response_status(self, request: Request, client_ip: str, status_code: int):
        """Обновление статуса ответа в истории"""
        try:
            request_key = f"requests:{client_ip}"
            requests_data = await self.redis.get(request_key)
            
            if requests_data:
                requests = json.loads(requests_data)
                if requests:
                    # Обновляем статус последнего запроса
                    requests[-1]["status_code"] = status_code
                    await self.redis.setex(request_key, 3600, json.dumps(requests))
                    
        except Exception as e:
            logger.error(f"Ошибка обновления статуса ответа: {e}")

# Функция для создания middleware
def create_threat_detection_middleware(redis_client: redis.Redis) -> ThreatDetectionMiddleware:
    return ThreatDetectionMiddleware(None, redis_client)


