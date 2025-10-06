import asyncio
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
import time
import psutil

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Асинхронный пул соединений для PostgreSQL"""
    
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self.async_session_maker = None
        self._connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "failed_connections": 0,
            "connection_errors": 0
        }
        self._performance_metrics = {
            "query_count": 0,
            "slow_queries": 0,
            "total_query_time": 0.0,
            "avg_query_time": 0.0
        }
    
    async def initialize(self):
        """Инициализация пула соединений"""
        try:
            # Создание асинхронного движка SQLAlchemy
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # Логирование SQL запросов
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Проверка соединений перед использованием
                pool_recycle=3600,   # Пересоздание соединений каждый час
                pool_timeout=30,     # Таймаут ожидания соединения
                pool_reset_on_return='commit'  # Сброс состояния соединения
            )
            
            # Создание фабрики сессий
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            # Настройка мониторинга
            await self._setup_monitoring()
            
            # Тестовое соединение
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            logger.info(f"Database connection pool initialized successfully. Pool size: {self.pool_size}, Max overflow: {self.max_overflow}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def _setup_monitoring(self):
        """Настройка мониторинга соединений"""
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            self._connection_stats["total_connections"] += 1
            self._connection_stats["active_connections"] += 1
            logger.debug(f"Database connection established. Total: {self._connection_stats['total_connections']}")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            self._connection_stats["idle_connections"] -= 1
            self._connection_stats["active_connections"] += 1
            logger.debug(f"Database connection checked out. Active: {self._connection_stats['active_connections']}")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            self._connection_stats["active_connections"] -= 1
            self._connection_stats["idle_connections"] += 1
            logger.debug(f"Database connection checked in. Idle: {self._connection_stats['idle_connections']}")
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_connection):
            self._connection_stats["active_connections"] -= 1
            logger.debug(f"Database connection closed. Active: {self._connection_stats['active_connections']}")
    
    @asynccontextmanager
    async def get_session(self):
        """Получение сессии из пула"""
        session = None
        start_time = time.time()
        
        try:
            session = self.async_session_maker()
            self._performance_metrics["query_count"] += 1
            
            yield session
            
        except Exception as e:
            self._connection_stats["connection_errors"] += 1
            logger.error(f"Database session error: {e}")
            if session:
                await session.rollback()
            raise
            
        finally:
            if session:
                query_time = time.time() - start_time
                self._performance_metrics["total_query_time"] += query_time
                self._performance_metrics["avg_query_time"] = (
                    self._performance_metrics["total_query_time"] / self._performance_metrics["query_count"]
                )
                
                # Логирование медленных запросов
                if query_time > 1.0:  # Больше 1 секунды
                    self._performance_metrics["slow_queries"] += 1
                    logger.warning(f"Slow query detected: {query_time:.2f}s")
                
                await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """Выполнение SQL запроса"""
        async with self.get_session() as session:
            try:
                if params:
                    result = await session.execute(query, params)
                else:
                    result = await session.execute(query)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise
    
    async def execute_transaction(self, queries: List[Dict[str, Any]]):
        """Выполнение транзакции с несколькими запросами"""
        async with self.get_session() as session:
            try:
                results = []
                for query_data in queries:
                    query = query_data["query"]
                    params = query_data.get("params", {})
                    result = await session.execute(query, params)
                    results.append(result)
                
                await session.commit()
                return results
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Получение статистики соединений"""
        if not self.engine:
            return {}
        
        try:
            pool = self.engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "total_connections": self._connection_stats["total_connections"],
                "active_connections": self._connection_stats["active_connections"],
                "idle_connections": self._connection_stats["idle_connections"],
                "failed_connections": self._connection_stats["failed_connections"],
                "connection_errors": self._connection_stats["connection_errors"]
            }
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        return {
            "query_count": self._performance_metrics["query_count"],
            "slow_queries": self._performance_metrics["slow_queries"],
            "total_query_time": round(self._performance_metrics["total_query_time"], 2),
            "avg_query_time": round(self._performance_metrics["avg_query_time"], 3),
            "slow_query_percentage": round(
                (self._performance_metrics["slow_queries"] / max(self._performance_metrics["query_count"], 1)) * 100, 2
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья пула соединений"""
        try:
            # Проверка соединения
            async with self.engine.begin() as conn:
                result = await conn.execute("SELECT 1 as health_check")
                row = result.fetchone()
                db_healthy = row[0] == 1 if row else False
            
            # Получение статистики
            conn_stats = await self.get_connection_stats()
            perf_metrics = await self.get_performance_metrics()
            
            # Проверка системных ресурсов
            system_info = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
            
            # Оценка здоровья
            health_score = 100
            if conn_stats.get("connection_errors", 0) > 10:
                health_score -= 20
            if perf_metrics.get("slow_query_percentage", 0) > 10:
                health_score -= 15
            if system_info["memory_percent"] > 80:
                health_score -= 10
            if system_info["cpu_percent"] > 80:
                health_score -= 10
            
            return {
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy",
                "health_score": health_score,
                "database_healthy": db_healthy,
                "connection_stats": conn_stats,
                "performance_metrics": perf_metrics,
                "system_info": system_info,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "health_score": 0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def optimize_pool(self):
        """Оптимизация пула соединений на основе статистики"""
        try:
            stats = await self.get_connection_stats()
            perf_metrics = await self.get_performance_metrics()
            
            current_pool_size = stats.get("pool_size", self.pool_size)
            current_overflow = stats.get("overflow", self.max_overflow)
            
            # Адаптивная настройка размера пула
            if stats.get("checked_out", 0) > current_pool_size * 0.8:
                # Много активных соединений - увеличиваем пул
                new_pool_size = min(current_pool_size + 5, 50)
                if new_pool_size != current_pool_size:
                    logger.info(f"Increasing pool size from {current_pool_size} to {new_pool_size}")
                    # В реальном проекте здесь нужно пересоздать engine
                    
            elif stats.get("checked_out", 0) < current_pool_size * 0.3:
                # Мало активных соединений - уменьшаем пул
                new_pool_size = max(current_pool_size - 2, 10)
                if new_pool_size != current_pool_size:
                    logger.info(f"Decreasing pool size from {current_pool_size} to {new_pool_size}")
                    # В реальном проекте здесь нужно пересоздать engine
            
            # Очистка неиспользуемых соединений
            if stats.get("invalid", 0) > 0:
                logger.info(f"Cleaning up {stats['invalid']} invalid connections")
                # В реальном проекте здесь нужно очистить недействительные соединения
                
        except Exception as e:
            logger.error(f"Pool optimization failed: {e}")
    
    async def close(self):
        """Закрытие пула соединений"""
        try:
            if self.engine:
                await self.engine.dispose()
                logger.info("Database connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")

# Глобальный экземпляр пула соединений
db_pool = DatabaseConnectionPool("postgresql+asyncpg://user:password@localhost/paygo")

# Функция для получения сессии
async def get_db_session():
    """Dependency для FastAPI для получения сессии БД"""
    async with db_pool.get_session() as session:
        yield session

# Функция для выполнения запросов
async def execute_db_query(query: str, params: Optional[Dict[str, Any]] = None):
    """Выполнение запроса к БД"""
    return await db_pool.execute_query(query, params)

# Функция для выполнения транзакций
async def execute_db_transaction(queries: List[Dict[str, Any]]):
    """Выполнение транзакции"""
    return await db_pool.execute_transaction(queries)


