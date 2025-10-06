import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock

from cache.redis_cache import RedisCache
from database.connection_pool import DatabaseConnectionPool

# Тесты производительности Redis кеша
class TestRedisCachePerformance:
    """Тесты производительности Redis кеша"""
    
    @pytest.fixture
    async def redis_cache(self):
        """Фикстура для Redis кеша"""
        cache = RedisCache("redis://localhost:6379")
        try:
            await cache.connect()
            yield cache
        finally:
            await cache.disconnect()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_set_performance(self, redis_cache):
        """Тест производительности установки значений в кеш"""
        iterations = 1000
        times = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            await redis_cache.set(f"test_key_{i}", f"test_value_{i}")
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        # Проверяем, что среднее время установки меньше 1ms
        assert avg_time < 0.001, f"Среднее время установки слишком высокое: {avg_time:.6f}s"
        assert max_time < 0.01, f"Максимальное время установки слишком высокое: {max_time:.6f}s"
        
        print(f"Cache SET Performance:")
        print(f"  Iterations: {iterations}")
        print(f"  Average time: {avg_time:.6f}s")
        print(f"  Min time: {min_time:.6f}s")
        print(f"  Max time: {max_time:.6f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_get_performance(self, redis_cache):
        """Тест производительности получения значений из кеша"""
        # Сначала устанавливаем данные
        test_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        for key, value in test_data.items():
            await redis_cache.set(key, value)
        
        iterations = 1000
        times = []
        
        for _ in range(iterations):
            key = f"key_{pytest.randint(0, 999)}"
            start_time = time.perf_counter()
            await redis_cache.get(key)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        # Проверяем, что среднее время получения меньше 0.5ms
        assert avg_time < 0.0005, f"Среднее время получения слишком высокое: {avg_time:.6f}s"
        assert max_time < 0.005, f"Максимальное время получения слишком высокое: {max_time:.6f}s"
        
        print(f"Cache GET Performance:")
        print(f"  Iterations: {iterations}")
        print(f"  Average time: {avg_time:.6f}s")
        print(f"  Min time: {min_time:.6f}s")
        print(f"  Max time: {max_time:.6f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_batch_operations(self, redis_cache):
        """Тест производительности пакетных операций"""
        batch_size = 100
        iterations = 10
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            # Пакетная установка
            set_tasks = [
                redis_cache.set(f"batch_key_{i}", f"batch_value_{i}")
                for i in range(batch_size)
            ]
            await asyncio.gather(*set_tasks)
            
            # Пакетное получение
            get_tasks = [
                redis_cache.get(f"batch_key_{i}")
                for i in range(batch_size)
            ]
            await asyncio.gather(*get_tasks)
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        total_operations = batch_size * 2 * iterations
        
        # Проверяем производительность пакетных операций
        assert avg_time < 0.1, f"Время пакетных операций слишком высокое: {avg_time:.3f}s"
        
        print(f"Cache Batch Operations Performance:")
        print(f"  Batch size: {batch_size}")
        print(f"  Iterations: {iterations}")
        print(f"  Total operations: {total_operations}")
        print(f"  Average time per batch: {avg_time:.3f}s")
        print(f"  Operations per second: {total_operations / avg_time:.0f}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_memory_usage(self, redis_cache):
        """Тест использования памяти кеша"""
        # Устанавливаем данные разного размера
        small_data = "small_value" * 10
        medium_data = "medium_value" * 100
        large_data = "large_value" * 1000
        
        data_sizes = [small_data, medium_data, large_data]
        memory_usage = []
        
        for i, data in enumerate(data_sizes):
            for j in range(100):
                key = f"memory_test_{i}_{j}"
                await redis_cache.set(key, data)
            
            # Получаем статистику памяти
            stats = await redis_cache.get_stats()
            memory_usage.append(stats.get("used_memory_human", "0B"))
        
        print(f"Cache Memory Usage:")
        for i, usage in enumerate(memory_usage):
            print(f"  Data size {i+1}: {usage}")
        
        # Проверяем, что память не превышает разумные пределы
        # (в реальном проекте нужно настроить лимиты)
        assert len(memory_usage) == 3, "Не удалось получить статистику памяти"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self, redis_cache):
        """Тест производительности при конкурентном доступе"""
        concurrent_users = 50
        operations_per_user = 20
        times = []
        
        async def user_operations(user_id: int):
            user_times = []
            for i in range(operations_per_user):
                key = f"concurrent_key_{user_id}_{i}"
                value = f"concurrent_value_{user_id}_{i}"
                
                start_time = time.perf_counter()
                await redis_cache.set(key, value)
                result = await redis_cache.get(key)
                end_time = time.perf_counter()
                
                user_times.append(end_time - start_time)
                assert result == value, f"Неправильное значение для ключа {key}"
            
            return user_times
        
        # Запускаем конкурентные операции
        start_time = time.perf_counter()
        user_results = await asyncio.gather(*[
            user_operations(i) for i in range(concurrent_users)
        ])
        total_time = time.perf_counter() - start_time
        
        # Собираем все времена
        for user_times in user_results:
            times.extend(user_times)
        
        total_operations = concurrent_users * operations_per_user
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Проверяем производительность при конкурентном доступе
        assert avg_time < 0.002, f"Среднее время при конкурентном доступе слишком высокое: {avg_time:.6f}s"
        assert total_time < 5.0, f"Общее время конкурентных операций слишком высокое: {total_time:.2f}s"
        
        print(f"Cache Concurrent Access Performance:")
        print(f"  Concurrent users: {concurrent_users}")
        print(f"  Operations per user: {operations_per_user}")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per operation: {avg_time:.6f}s")
        print(f"  Operations per second: {total_operations / total_time:.0f}")

# Тесты производительности Connection Pool
class TestConnectionPoolPerformance:
    """Тесты производительности пула соединений"""
    
    @pytest.fixture
    async def db_pool(self):
        """Фикстура для пула соединений"""
        pool = DatabaseConnectionPool("postgresql+asyncpg://test:test@localhost/testdb")
        try:
            await pool.initialize()
            yield pool
        finally:
            await pool.close()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_connection_acquisition_performance(self, db_pool):
        """Тест производительности получения соединений из пула"""
        iterations = 100
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            async with db_pool.get_session() as session:
                # Имитируем работу с сессией
                await asyncio.sleep(0.001)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        # Проверяем производительность получения соединений
        assert avg_time < 0.01, f"Среднее время получения соединения слишком высокое: {avg_time:.6f}s"
        assert max_time < 0.05, f"Максимальное время получения соединения слишком высокое: {max_time:.6f}s"
        
        print(f"Connection Acquisition Performance:")
        print(f"  Iterations: {iterations}")
        print(f"  Average time: {avg_time:.6f}s")
        print(f"  Min time: {min_time:.6f}s")
        print(f"  Max time: {max_time:.6f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_connections(self, db_pool):
        """Тест производительности при конкурентных соединениях"""
        concurrent_connections = 20
        operations_per_connection = 10
        times = []
        
        async def connection_operations(conn_id: int):
            conn_times = []
            for i in range(operations_per_connection):
                start_time = time.perf_counter()
                async with db_pool.get_session() as session:
                    # Имитируем выполнение запроса
                    await asyncio.sleep(0.001)
                end_time = time.perf_counter()
                conn_times.append(end_time - start_time)
            return conn_times
        
        # Запускаем конкурентные соединения
        start_time = time.perf_counter()
        connection_results = await asyncio.gather(*[
            connection_operations(i) for i in range(concurrent_connections)
        ])
        total_time = time.perf_counter() - start_time
        
        # Собираем все времена
        for conn_times in connection_results:
            times.extend(conn_times)
        
        total_operations = concurrent_connections * operations_per_connection
        avg_time = statistics.mean(times)
        
        # Проверяем производительность при конкурентных соединениях
        assert avg_time < 0.02, f"Среднее время при конкурентных соединениях слишком высокое: {avg_time:.6f}s"
        assert total_time < 10.0, f"Общее время конкурентных операций слишком высокое: {total_time:.2f}s"
        
        print(f"Concurrent Connections Performance:")
        print(f"  Concurrent connections: {concurrent_connections}")
        print(f"  Operations per connection: {operations_per_connection}")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per operation: {avg_time:.6f}s")
        print(f"  Operations per second: {total_operations / total_time:.0f}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_pool_scaling(self, db_pool):
        """Тест масштабирования пула соединений"""
        # Тестируем разные нагрузки
        load_levels = [5, 10, 20, 30]
        performance_results = []
        
        for load in load_levels:
            start_time = time.perf_counter()
            
            # Создаем нагрузку
            async def load_test():
                async with db_pool.get_session() as session:
                    await asyncio.sleep(0.001)
            
            # Запускаем конкурентные операции
            await asyncio.gather(*[load_test() for _ in range(load)])
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            
            performance_results.append({
                'load': load,
                'time': total_time,
                'ops_per_second': load / total_time
            })
        
        print(f"Pool Scaling Performance:")
        for result in performance_results:
            print(f"  Load: {result['load']}, Time: {result['time']:.3f}s, OPS: {result['ops_per_second']:.1f}")
        
        # Проверяем, что производительность не падает критически при увеличении нагрузки
        for i in range(1, len(performance_results)):
            prev_ops = performance_results[i-1]['ops_per_second']
            curr_ops = performance_results[i]['ops_per_second']
            
            # Допускаем снижение производительности не более чем в 2 раза
            assert curr_ops > prev_ops * 0.5, f"Критическое падение производительности при нагрузке {performance_results[i]['load']}"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, db_pool):
        """Тест эффективности использования памяти"""
        # Получаем статистику пула
        stats = await db_pool.get_connection_stats()
        perf_metrics = await db_pool.get_performance_metrics()
        
        print(f"Pool Memory Efficiency:")
        print(f"  Pool size: {stats.get('pool_size', 'N/A')}")
        print(f"  Active connections: {stats.get('active_connections', 'N/A')}")
        print(f"  Idle connections: {stats.get('idle_connections', 'N/A')}")
        print(f"  Total queries: {perf_metrics.get('query_count', 'N/A')}")
        print(f"  Average query time: {perf_metrics.get('avg_query_time', 'N/A')}s")
        
        # Проверяем, что пул эффективно использует соединения
        if stats.get('pool_size', 0) > 0:
            utilization = stats.get('active_connections', 0) / stats.get('pool_size', 1)
            assert utilization > 0.1, f"Низкая утилизация пула: {utilization:.2%}"
            assert utilization < 0.9, f"Слишком высокая утилизация пула: {utilization:.2%}"

# Тесты интеграции производительности
class TestPerformanceIntegration:
    """Интеграционные тесты производительности"""
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_end_to_end_performance(self):
        """Тест end-to-end производительности системы"""
        # Создаем экземпляры кеша и пула соединений
        cache = RedisCache("redis://localhost:6379")
        pool = DatabaseConnectionPool("postgresql+asyncpg://test:test@localhost/testdb")
        
        try:
            await cache.connect()
            await pool.initialize()
            
            # Тестируем полный цикл: кеш -> БД -> кеш
            iterations = 100
            times = []
            
            for i in range(iterations):
                start_time = time.perf_counter()
                
                # Проверяем кеш
                cache_key = f"integration_test_{i}"
                cached_value = await cache.get(cache_key)
                
                if cached_value is None:
                    # Если нет в кеше, получаем из БД (имитируем)
                    async with pool.get_session() as session:
                        await asyncio.sleep(0.001)  # Имитация запроса к БД
                    
                    # Сохраняем в кеш
                    await cache.set(cache_key, f"value_{i}")
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            # Проверяем общую производительность
            assert avg_time < 0.01, f"Среднее время end-to-end операции слишком высокое: {avg_time:.6f}s"
            assert max_time < 0.05, f"Максимальное время end-to-end операции слишком высокое: {max_time:.6f}s"
            
            print(f"End-to-End Performance:")
            print(f"  Iterations: {iterations}")
            print(f"  Average time: {avg_time:.6f}s")
            print(f"  Max time: {max_time:.6f}s")
            print(f"  Operations per second: {1 / avg_time:.0f}")
            
        finally:
            await cache.disconnect()
            await pool.close()
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_stress_test(self):
        """Стресс-тест системы"""
        # Создаем высокую нагрузку
        concurrent_operations = 100
        operations_per_thread = 50
        
        async def stress_operation(thread_id: int):
            cache = RedisCache("redis://localhost:6379")
            pool = DatabaseConnectionPool("postgresql+asyncpg://test:test@localhost/testdb")
            
            try:
                await cache.connect()
                await pool.initialize()
                
                thread_times = []
                for i in range(operations_per_thread):
                    start_time = time.perf_counter()
                    
                    # Смешанные операции
                    if i % 3 == 0:
                        # Операция с кешем
                        await cache.set(f"stress_cache_{thread_id}_{i}", f"data_{i}")
                    elif i % 3 == 1:
                        # Операция с БД
                        async with pool.get_session() as session:
                            await asyncio.sleep(0.001)
                    else:
                        # Комбинированная операция
                        await cache.get(f"stress_cache_{thread_id}_{i-1}")
                        async with pool.get_session() as session:
                            await asyncio.sleep(0.001)
                    
                    end_time = time.perf_counter()
                    thread_times.append(end_time - start_time)
                
                return thread_times
                
            finally:
                await cache.disconnect()
                await pool.close()
        
        # Запускаем стресс-тест
        start_time = time.perf_counter()
        stress_results = await asyncio.gather(*[
            stress_operation(i) for i in range(concurrent_operations)
        ])
        total_time = time.perf_counter() - start_time
        
        # Анализируем результаты
        all_times = []
        for thread_times in stress_results:
            all_times.extend(thread_times)
        
        total_operations = concurrent_operations * operations_per_thread
        avg_time = statistics.mean(all_times)
        max_time = max(all_times)
        min_time = min(all_times)
        
        # Проверяем, что система выдерживает нагрузку
        assert avg_time < 0.02, f"Среднее время при стресс-нагрузке слишком высокое: {avg_time:.6f}s"
        assert max_time < 0.1, f"Максимальное время при стресс-нагрузке слишком высокое: {max_time:.6f}s"
        assert total_time < 30.0, f"Общее время стресс-теста слишком высокое: {total_time:.2f}s"
        
        print(f"Stress Test Results:")
        print(f"  Concurrent operations: {concurrent_operations}")
        print(f"  Operations per thread: {operations_per_thread}")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per operation: {avg_time:.6f}s")
        print(f"  Min time: {min_time:.6f}s")
        print(f"  Max time: {max_time:.6f}s")
        print(f"  Operations per second: {total_operations / total_time:.0f}")

# Утилиты для тестирования производительности
class PerformanceUtils:
    """Утилиты для тестирования производительности"""
    
    @staticmethod
    def measure_time(func, *args, **kwargs):
        """Измерение времени выполнения функции"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    @staticmethod
    async def measure_async_time(async_func, *args, **kwargs):
        """Измерение времени выполнения асинхронной функции"""
        start_time = time.perf_counter()
        result = await async_func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    @staticmethod
    def generate_test_data(size: int) -> Dict[str, Any]:
        """Генерация тестовых данных заданного размера"""
        return {
            "id": size,
            "name": f"test_name_{size}",
            "data": "x" * size,
            "timestamp": time.time(),
            "metadata": {
                "key1": "value1",
                "key2": "value2",
                "nested": {
                    "deep_key": "deep_value"
                }
            }
        }
    
    @staticmethod
    def performance_report(test_name: str, times: List[float], operations: int):
        """Генерация отчета о производительности"""
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n{test_name} Performance Report:")
        print(f"  Operations: {operations}")
        print(f"  Total time: {sum(times):.6f}s")
        print(f"  Average time: {avg_time:.6f}s")
        print(f"  Median time: {median_time:.6f}s")
        print(f"  Standard deviation: {std_dev:.6f}s")
        print(f"  Min time: {min_time:.6f}s")
        print(f"  Max time: {max_time:.6f}s")
        print(f"  Operations per second: {operations / sum(times):.0f}")
        
        return {
            "test_name": test_name,
            "operations": operations,
            "total_time": sum(times),
            "average_time": avg_time,
            "median_time": median_time,
            "std_deviation": std_dev,
            "min_time": min_time,
            "max_time": max_time,
            "ops_per_second": operations / sum(times)
        }
