import asyncio
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    TRANSACTION_SUCCESS = "transaction_success"
    TRANSACTION_FAILED = "transaction_failed"
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"
    PAYMENT_REMINDER = "payment_reminder"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict] = None
    created_at: datetime = datetime.now()
    sent_at: Optional[datetime] = None
    is_read: bool = False

class PushNotificationService:
    def __init__(self):
        self.web_subscriptions: Dict[str, List[str]] = {}  # user_id -> [subscription_ids]
        self.mobile_tokens: Dict[str, List[str]] = {}      # user_id -> [device_tokens]
        
    async def subscribe_web_push(self, user_id: str, subscription_info: str):
        """Подписка на веб-push уведомления"""
        if user_id not in self.web_subscriptions:
            self.web_subscriptions[user_id] = []
        
        if subscription_info not in self.web_subscriptions[user_id]:
            self.web_subscriptions[user_id].append(subscription_info)
            logger.info(f"✅ Пользователь {user_id} подписался на веб-push уведомления")
    
    async def subscribe_mobile_push(self, user_id: str, device_token: str):
        """Подписка на мобильные push уведомления"""
        if user_id not in self.mobile_tokens:
            self.mobile_tokens[user_id] = []
        
        if device_token not in self.mobile_tokens[user_id]:
            self.mobile_tokens[user_id].append(device_token)
            logger.info(f"✅ Пользователь {user_id} подписался на мобильные push уведомления")
    
    async def send_web_push(self, user_id: str, notification: Notification):
        """Отправка веб-push уведомления"""
        if user_id not in self.web_subscriptions:
            return False
        
        success_count = 0
        for subscription in self.web_subscriptions[user_id]:
            try:
                # Здесь должна быть интеграция с реальным сервисом (например, web-push)
                # Для примера используем заглушку
                await self._send_web_push_impl(subscription, notification)
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки веб-push для {user_id}: {e}")
        
        logger.info(f"📱 Отправлено {success_count} веб-push уведомлений пользователю {user_id}")
        return success_count > 0
    
    async def send_mobile_push(self, user_id: str, notification: Notification):
        """Отправка мобильного push уведомления"""
        if user_id not in self.mobile_tokens:
            return False
        
        success_count = 0
        for token in self.mobile_tokens[user_id]:
            try:
                # Здесь должна быть интеграция с FCM (Firebase Cloud Messaging)
                await self._send_fcm_push(token, notification)
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Ошибка отправки FCM для {user_id}: {e}")
        
        logger.info(f"📱 Отправлено {success_count} мобильных push уведомлений пользователю {user_id}")
        return success_count > 0
    
    async def send_notification(self, user_id: str, notification: Notification):
        """Отправка уведомления всеми доступными способами"""
        tasks = []
        
        # Отправка веб-push
        if user_id in self.web_subscriptions:
            tasks.append(self.send_web_push(user_id, notification))
        
        # Отправка мобильного push
        if user_id in self.mobile_tokens:
            tasks.append(self.send_mobile_push(user_id, notification))
        
        # Выполняем все задачи параллельно
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success = any(result for result in results if isinstance(result, bool) and result)
            
            if success:
                notification.sent_at = datetime.now()
                logger.info(f"✅ Уведомление отправлено пользователю {user_id}")
            else:
                logger.warning(f"⚠️ Не удалось отправить уведомление пользователю {user_id}")
            
            return success
        
        return False
    
    async def send_bulk_notifications(self, user_ids: List[str], notification: Notification):
        """Массовая отправка уведомлений"""
        tasks = [self.send_notification(user_id, notification) for user_id in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if isinstance(result, bool) and result)
        logger.info(f"📢 Массовая отправка: {success_count}/{len(user_ids)} успешно")
        
        return success_count
    
    async def _send_web_push_impl(self, subscription: str, notification: Notification):
        """Реализация отправки веб-push (заглушка)"""
        # В реальном проекте здесь будет интеграция с web-push библиотекой
        await asyncio.sleep(0.1)  # Имитация отправки
        logger.debug(f"🌐 Веб-push отправлен: {notification.title}")
    
    async def _send_fcm_push(self, token: str, notification: Notification):
        """Реализация отправки FCM push (заглушка)"""
        # В реальном проекте здесь будет интеграция с Firebase
        await asyncio.sleep(0.1)  # Имитация отправки
        logger.debug(f"📱 FCM push отправлен: {notification.title}")
    
    def get_user_subscriptions(self, user_id: str) -> Dict:
        """Получение информации о подписках пользователя"""
        return {
            "web_push": len(self.web_subscriptions.get(user_id, [])),
            "mobile_push": len(self.mobile_tokens.get(user_id, [])),
            "total": len(self.web_subscriptions.get(user_id, [])) + len(self.mobile_tokens.get(user_id, []))
        }
    
    async def unsubscribe_web_push(self, user_id: str, subscription_info: str):
        """Отписка от веб-push уведомлений"""
        if user_id in self.web_subscriptions and subscription_info in self.web_subscriptions[user_id]:
            self.web_subscriptions[user_id].remove(subscription_info)
            logger.info(f"❌ Пользователь {user_id} отписался от веб-push уведомлений")
    
    async def unsubscribe_mobile_push(self, user_id: str, device_token: str):
        """Отписка от мобильных push уведомлений"""
        if user_id in self.mobile_tokens and device_token in self.mobile_tokens[user_id]:
            self.mobile_tokens[user_id].remove(device_token)
            logger.info(f"❌ Пользователь {user_id} отписался от мобильных push уведомлений")

# Глобальный экземпляр сервиса
notification_service = PushNotificationService()

