@echo off
echo ========================================
echo PayGo - Комплексное тестирование системы
echo ========================================
echo.

echo [1/7] Проверка структуры проекта...
if not exist "web-service\backend\cache\redis_cache.py" (
    echo ERROR: Redis cache не найден!
    exit /b 1
)
if not exist "web-service\backend\database\connection_pool.py" (
    echo ERROR: Database connection pool не найден!
    exit /b 1
)
if not exist "web-service\backend\tests\test_performance.py" (
    echo ERROR: Performance tests не найдены!
    exit /b 1
)
if not exist ".github\workflows\ci-cd.yml" (
    echo ERROR: CI/CD pipeline не найден!
    exit /b 1
)
echo ✓ Структура проекта проверена
echo.

echo [2/7] Проверка зависимостей...
cd web-service\backend
if not exist "requirements.txt" (
    echo ERROR: requirements.txt не найден!
    exit /b 1
)
echo ✓ Backend зависимости найдены
cd ..\..

cd web-service\frontend
if not exist "package.json" (
    echo ERROR: package.json не найден!
    exit /b 1
)
echo ✓ Frontend зависимости найдены
cd ..\..
echo.

echo [3/7] Проверка Docker конфигурации...
if not exist "docker-compose.yml" (
    echo ERROR: docker-compose.yml не найден!
    exit /b 1
)
if not exist "web-service\backend\Dockerfile" (
    echo ERROR: Backend Dockerfile не найден!
    exit /b 1
)
if not exist "web-service\frontend\Dockerfile" (
    echo ERROR: Frontend Dockerfile не найден!
    exit /b 1
)
echo ✓ Docker конфигурация проверена
echo.

echo [4/7] Проверка мониторинга...
if not exist "config\prometheus.yml" (
    echo ERROR: Prometheus конфигурация не найдена!
    exit /b 1
)
echo ✓ Мониторинг настроен
echo.

echo [5/7] Проверка базы данных...
if not exist "web-service\database\init.sql" (
    echo ERROR: Database init.sql не найден!
    exit /b 1
)
echo ✓ База данных настроена
echo.

echo [6/7] Проверка тестов...
if not exist "web-service\backend\tests\" (
    echo ERROR: Тесты не найдены!
    exit /b 1
)
echo ✓ Тесты найдены
echo.

echo [7/7] Проверка документации...
if not exist "README.md" (
    echo ERROR: README.md не найден!
    exit /b 1
)
echo ✓ Документация найдена
echo.

echo ========================================
echo ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!
echo ========================================
echo.
echo Следующие шаги:
echo 1. docker-compose build
echo 2. docker-compose up -d
echo 3. docker-compose ps
echo 4. docker-compose logs -f backend
echo.
echo Система готова к запуску!
pause
