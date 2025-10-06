import json
import pickle
from typing import Any, Optional, Union, Dict, List
import aioredis
from datetime import datetime, timedelta
import logging
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

class RedisCache:
    """Расширенный Redis кеш с поддержкой сессий, данных и различных стратегий"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.default_ttl = 3600  # 1 час по умолчанию
        
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # Для поддержки pickle
            )
            await self.redis.ping()
            logger.info("Redis подключен успешно")
        except Exception as e:
            logger.error(f"Ошибка подключения к Redis: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis отключен")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  strategy: str = "default") -> bool:
        """Установка значения в кеш"""
        try:
            if not self.redis:
                return False
                
            ttl = ttl or self.default_ttl
            
            if strategy == "json":
                serialized = json.dumps(value, default=str).encode()
            elif strategy == "pickle":
                serialized = pickle.dumps(value)
            else:
                serialized = str(value).encode()
            
            result = await self.redis.setex(key, ttl, serialized)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка установки кеша {key}: {e}")
            return False
    
    async def get(self, key: str, strategy: str = "default") -> Optional[Any]:
        """Получение значения из кеша"""
        try:
            if not self.redis:
                return None
                
            value = await self.redis.get(key)
            if value is None:
                return None
            
            if strategy == "json":
                return json.loads(value.decode())
            elif strategy == "pickle":
                return pickle.loads(value)
            else:
                return value.decode()
        except Exception as e:
            logger.error(f"Ошибка получения кеша {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Удаление ключа из кеша"""
        try:
            if not self.redis:
                return False
            result = await self.redis.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка удаления кеша {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        try:
            if not self.redis:
                return False
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка проверки ключа {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Установка TTL для ключа"""
        try:
            if not self.redis:
                return False
            result = await self.redis.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка установки TTL для {key}: {e}")
            return False
    
    # Методы для работы с сессиями
    async def set_session(self, session_id: str, user_data: Dict, ttl: int = 3600) -> bool:
        """Установка сессии пользователя"""
        key = f"session:{session_id}"
        return await self.set(key, user_data, ttl, "json")
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Получение сессии пользователя"""
        key = f"session:{session_id}"
        return await self.get(key, "json")
    
    async def delete_session(self, session_id: str) -> bool:
        """Удаление сессии пользователя"""
        key = f"session:{session_id}"
        return await self.delete(key)
    
    # Методы для работы с данными
    async def set_data(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Кеширование данных с автоматическим выбором стратегии"""
        if isinstance(data, (dict, list)):
            return await self.set(key, data, ttl, "json")
        else:
            return await self.set(key, data, ttl, "pickle")
    
    async def get_data(self, key: str) -> Optional[Any]:
        """Получение данных с автоматическим определением типа"""
        try:
            if not self.redis:
                return None
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Пробуем разные стратегии десериализации
            try:
                return json.loads(value.decode())
            except:
                try:
                    return pickle.loads(value)
                except:
                    return value.decode()
        except Exception as e:
            logger.error(f"Ошибка получения данных {key}: {e}")
            return None
    
    # Методы для работы с хеш-таблицами
    async def hset(self, name: str, key: str, value: Any) -> bool:
        """Установка значения в хеш-таблицу"""
        try:
            if not self.redis:
                return False
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value, default=str)
            else:
                serialized = str(value)
            result = await self.redis.hset(name, key, serialized)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка установки хеша {name}:{key}: {e}")
            return False
    
    async def hget(self, name: str, key: str) -> Optional[Any]:
        """Получение значения из хеш-таблицы"""
        try:
            if not self.redis:
                return None
            value = await self.redis.hget(name, key)
            if value is None:
                return None
            
            try:
                return json.loads(value.decode())
            except:
                return value.decode()
        except Exception as e:
            logger.error(f"Ошибка получения хеша {name}:{key}: {e}")
            return None
    
    # Методы для работы со списками
    async def lpush(self, name: str, value: Any) -> bool:
        """Добавление элемента в начало списка"""
        try:
            if not self.redis:
                return False
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value, default=str)
            else:
                serialized = str(value)
            result = await self.redis.lpush(name, serialized)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка добавления в список {name}: {e}")
            return False
    
    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Получение элементов списка"""
        try:
            if not self.redis:
                return []
            values = await self.redis.lrange(name, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value.decode()))
                except:
                    result.append(value.decode())
            return result
        except Exception as e:
            logger.error(f"Ошибка получения списка {name}: {e}")
            return []
    
    # Методы для работы с множествами
    async def sadd(self, name: str, value: Any) -> bool:
        """Добавление элемента в множество"""
        try:
            if not self.redis:
                return False
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value, default=str)
            else:
                serialized = str(value)
            result = await self.redis.sadd(name, serialized)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка добавления в множество {name}: {e}")
            return False
    
    async def smembers(self, name: str) -> List[Any]:
        """Получение элементов множества"""
        try:
            if not self.redis:
                return []
            values = await self.redis.smembers(name)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value.decode()))
                except:
                    result.append(value.decode())
            return result
        except Exception as e:
            logger.error(f"Ошибка получения множества {name}: {e}")
            return []
    
    # Методы для работы с отсортированными множествами
    async def zadd(self, name: str, mapping: Dict[str, float]) -> bool:
        """Добавление элементов в отсортированное множество"""
        try:
            if not self.redis:
                return False
            result = await self.redis.zadd(name, mapping)
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка добавления в отсортированное множество {name}: {e}")
            return False
    
    async def zrange(self, name: str, start: int = 0, end: int = -1, 
                     desc: bool = False) -> List[str]:
        """Получение элементов отсортированного множества"""
        try:
            if not self.redis:
                return []
            if desc:
                result = await self.redis.zrevrange(name, start, end)
            else:
                result = await self.redis.zrange(name, start, end)
            return [item.decode() for item in result]
        except Exception as e:
            logger.error(f"Ошибка получения отсортированного множества {name}: {e}")
            return []
    
    # Методы для работы с ключами
    async def keys(self, pattern: str = "*") -> List[str]:
        """Поиск ключей по паттерну"""
        try:
            if not self.redis:
                return []
            keys = await self.redis.keys(pattern)
            return [key.decode() for key in keys]
        except Exception as e:
            logger.error(f"Ошибка поиска ключей {pattern}: {e}")
            return []
    
    async def delete_pattern(self, pattern: str) -> int:
        """Удаление ключей по паттерну"""
        try:
            if not self.redis:
                return 0
            keys = await self.redis.keys(pattern)
            if keys:
                result = await self.redis.delete(*keys)
                return result
            return 0
        except Exception as e:
            logger.error(f"Ошибка удаления ключей по паттерну {pattern}: {e}")
            return 0
    
    # Методы для статистики
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики Redis"""
        try:
            if not self.redis:
                return {}
            
            info = await self.redis.info()
            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
            # Расчет hit rate
            total_requests = stats["keyspace_hits"] + stats["keyspace_misses"]
            if total_requests > 0:
                stats["hit_rate"] = round(stats["keyspace_hits"] / total_requests * 100, 2)
            else:
                stats["hit_rate"] = 0
                
            return stats
        except Exception as e:
            logger.error(f"Ошибка получения статистики Redis: {e}")
            return {}

# Декоратор для кеширования функций
def cache_result(ttl: int = 3600, key_prefix: str = "", strategy: str = "default"):
    """Декоратор для кеширования результатов функций"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создание ключа кеша
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(str(args) + str(kwargs).encode()).hexdigest()}"
            
            # Получение экземпляра кеша (предполагается, что он доступен глобально)
            from cache.redis_cache import redis_cache
            
            # Попытка получить из кеша
            cached_result = await redis_cache.get_data(cache_key)
            if cached_result is not None:
                logger.debug(f"Кеш-хит для {cache_key}")
                return cached_result
            
            # Выполнение функции
            result = await func(*args, **kwargs)
            
            # Сохранение в кеш
            await redis_cache.set_data(cache_key, result, ttl)
            logger.debug(f"Кеш-мисс для {cache_key}, результат сохранен")
            
            return result
        return wrapper
    return decorator

# Глобальный экземпляр кеша
redis_cache = RedisCache()


