import pyotp
import qrcode
import io
import base64
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Enum
from pydantic import BaseModel, EmailStr
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class TwoFactorMethod(str, Enum):
    TOTP = "totp"      # Time-based One-Time Password
    SMS = "sms"        # SMS код
    EMAIL = "email"    # Email код
    BACKUP_CODES = "backup_codes"  # Резервные коды

class TwoFactorConfig(BaseModel):
    # TOTP настройки
    totp_issuer: str = "PayGo"
    totp_algorithm: str = "sha1"
    totp_digits: int = 6
    totp_period: int = 30  # секунд
    
    # SMS настройки
    sms_provider: str = "twilio"  # twilio, sms.ru, etc.
    sms_code_length: int = 6
    sms_expiry_minutes: int = 5
    
    # Email настройки
    email_code_length: int = 6
    email_expiry_minutes: int = 10
    
    # Общие настройки
    max_attempts: int = 3
    lockout_duration_minutes: int = 15
    backup_codes_count: int = 10

class TOTPService:
    def __init__(self, config: TwoFactorConfig):
        self.config = config
    
    def generate_secret(self) -> str:
        """Генерация секретного ключа для TOTP"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Генерация QR кода для TOTP приложения"""
        try:
            # Создаем URI для TOTP
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name=self.config.totp_issuer
            )
            
            # Генерируем QR код
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Создаем изображение
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Конвертируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Ошибка генерации QR кода: {e}")
            return ""
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Проверка TOTP токена"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token)
        except Exception as e:
            logger.error(f"Ошибка проверки TOTP: {e}")
            return False
    
    def get_current_totp(self, secret: str) -> str:
        """Получение текущего TOTP токена (для тестирования)"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            logger.error(f"Ошибка получения TOTP: {e}")
            return ""

class SMSService:
    def __init__(self, config: TwoFactorConfig):
        self.config = config
        self.sms_codes: Dict[str, Dict[str, Any]] = {}  # phone -> {code, expires, attempts}
    
    def generate_sms_code(self) -> str:
        """Генерация SMS кода"""
        return ''.join(secrets.choice('0123456789') for _ in range(self.config.sms_code_length))
    
    async def send_sms_code(self, phone: str, code: str) -> bool:
        """Отправка SMS кода"""
        try:
            # Здесь должна быть интеграция с реальным SMS провайдером
            # Для примера используем заглушку
            
            # Сохраняем код
            self.sms_codes[phone] = {
                "code": code,
                "expires": datetime.now() + timedelta(minutes=self.config.sms_expiry_minutes),
                "attempts": 0
            }
            
            logger.info(f"📱 SMS код {code} отправлен на {phone}")
            
            # В реальном проекте здесь будет вызов SMS API
            await self._send_sms_via_provider(phone, code)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки SMS: {e}")
            return False
    
    async def _send_sms_via_provider(self, phone: str, code: str):
        """Отправка SMS через провайдера (заглушка)"""
        # Имитация отправки
        await asyncio.sleep(0.1)
        
        # В реальном проекте здесь будет код для:
        # - Twilio
        # - SMS.ru
        # - Других провайдеров
        
        logger.debug(f"SMS отправлен через {self.config.sms_provider}: {phone} -> {code}")
    
    def verify_sms_code(self, phone: str, code: str) -> bool:
        """Проверка SMS кода"""
        if phone not in self.sms_codes:
            return False
        
        sms_data = self.sms_codes[phone]
        
        # Проверяем срок действия
        if datetime.now() > sms_data["expires"]:
            del self.sms_codes[phone]
            return False
        
        # Проверяем количество попыток
        if sms_data["attempts"] >= self.config.max_attempts:
            del self.sms_codes[phone]
            return False
        
        # Увеличиваем счетчик попыток
        sms_data["attempts"] += 1
        
        # Проверяем код
        if sms_data["code"] == code:
            del self.sms_codes[phone]  # Удаляем использованный код
            return True
        
        return False

class EmailService:
    def __init__(self, config: TwoFactorConfig):
        self.config = config
        self.email_codes: Dict[str, Dict[str, Any]] = {}  # email -> {code, expires, attempts}
    
    def generate_email_code(self) -> str:
        """Генерация email кода"""
        return ''.join(secrets.choice('0123456789') for _ in range(self.config.email_code_length))
    
    async def send_email_code(self, email: str, code: str) -> bool:
        """Отправка email кода"""
        try:
            # Сохраняем код
            self.email_codes[email] = {
                "code": code,
                "expires": datetime.now() + timedelta(minutes=self.config.email_expiry_minutes),
                "attempts": 0
            }
            
            logger.info(f"📧 Email код {code} отправлен на {email}")
            
            # В реальном проекте здесь будет отправка email
            await self._send_email_via_smtp(email, code)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email: {e}")
            return False
    
    async def _send_email_via_smtp(self, email: str, code: str):
        """Отправка email через SMTP (заглушка)"""
        # Имитация отправки
        await asyncio.sleep(0.1)
        
        # В реальном проекте здесь будет код для отправки email
        logger.debug(f"Email отправлен: {email} -> {code}")
    
    def verify_email_code(self, email: str, code: str) -> bool:
        """Проверка email кода"""
        if email not in self.email_codes:
            return False
        
        email_data = self.email_codes[email]
        
        # Проверяем срок действия
        if datetime.now() > email_data["expires"]:
            del self.email_codes[email]
            return False
        
        # Проверяем количество попыток
        if email_data["attempts"] >= self.config.max_attempts:
            del self.email_codes[email]
            return False
        
        # Увеличиваем счетчик попыток
        email_data["attempts"] += 1
        
        # Проверяем код
        if email_data["code"] == code:
            del self.email_codes[email]  # Удаляем использованный код
            return True
        
        return False

class BackupCodesService:
    def __init__(self, config: TwoFactorConfig):
        self.config = config
    
    def generate_backup_codes(self) -> list[str]:
        """Генерация резервных кодов"""
        codes = []
        for _ in range(self.config.backup_codes_count):
            # Генерируем код формата: XXXX-XXXX
            code = f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
            codes.append(code)
        return codes
    
    def verify_backup_code(self, stored_codes: list[str], provided_code: str) -> tuple[bool, list[str]]:
        """Проверка резервного кода"""
        # Нормализуем код (убираем дефисы и приводим к верхнему регистру)
        normalized_code = provided_code.replace('-', '').upper()
        
        for i, code in enumerate(stored_codes):
            if code.replace('-', '').upper() == normalized_code:
                # Удаляем использованный код
                remaining_codes = stored_codes[:i] + stored_codes[i+1:]
                return True, remaining_codes
        
        return False, stored_codes

class TwoFactorAuth:
    def __init__(self, config: TwoFactorConfig):
        self.config = config
        self.totp_service = TOTPService(config)
        self.sms_service = SMSService(config)
        self.email_service = EmailService(config)
        self.backup_codes_service = BackupCodesService(config)
        
        # Кэш заблокированных пользователей
        self.locked_users: Dict[str, Dict[str, Any]] = {}
    
    async def setup_totp(self, user_id: str, user_email: str) -> Dict[str, str]:
        """Настройка TOTP для пользователя"""
        try:
            secret = self.totp_service.generate_secret()
            qr_code = self.totp_service.generate_qr_code(secret, user_email)
            
            return {
                "secret": secret,
                "qr_code": qr_code,
                "backup_codes": self.backup_codes_service.generate_backup_codes()
            }
            
        except Exception as e:
            logger.error(f"Ошибка настройки TOTP для {user_id}: {e}")
            raise
    
    async def send_sms_code(self, phone: str) -> bool:
        """Отправка SMS кода"""
        code = self.sms_service.generate_sms_code()
        return await self.sms_service.send_sms_code(phone, code)
    
    async def send_email_code(self, email: str) -> bool:
        """Отправка email кода"""
        code = self.email_service.generate_email_code()
        return await self.email_service.send_email_code(email, code)
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Проверка TOTP токена"""
        return self.totp_service.verify_totp(secret, token)
    
    def verify_sms_code(self, phone: str, code: str) -> bool:
        """Проверка SMS кода"""
        return self.sms_service.verify_sms_code(phone, code)
    
    def verify_email_code(self, email: str, code: str) -> bool:
        """Проверка email кода"""
        return self.email_service.verify_email_code(email, code)
    
    def verify_backup_code(self, stored_codes: list[str], provided_code: str) -> tuple[bool, list[str]]:
        """Проверка резервного кода"""
        return self.backup_codes_service.verify_backup_code(stored_codes, provided_code)
    
    def is_user_locked(self, user_id: str) -> bool:
        """Проверка блокировки пользователя"""
        if user_id in self.locked_users:
            lock_info = self.locked_users[user_id]
            if datetime.now() < lock_info["until"]:
                return True
            else:
                del self.locked_users[user_id]
        return False
    
    def lock_user(self, user_id: str, reason: str = "too_many_attempts"):
        """Блокировка пользователя"""
        lock_until = datetime.now() + timedelta(minutes=self.config.lockout_duration_minutes)
        self.locked_users[user_id] = {
            "until": lock_until,
            "reason": reason
        }
        logger.warning(f"Пользователь {user_id} заблокирован: {reason}")
    
    def get_remaining_attempts(self, user_id: str) -> int:
        """Получение оставшихся попыток"""
        if user_id in self.locked_users:
            return 0
        return self.config.max_attempts

# Глобальная конфигурация 2FA
two_factor_config = TwoFactorConfig()

# Глобальный экземпляр 2FA сервиса
two_factor_auth = TwoFactorAuth(two_factor_config)


