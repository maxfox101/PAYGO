@echo off
echo ========================================
echo PayGo - Проверка здоровья системы
echo ========================================
echo.

echo [1/8] Проверка Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker не установлен или не доступен!
    pause
    exit /b 1
)
echo ✓ Docker доступен

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose не установлен!
    pause
    exit /b 1
)
echo ✓ Docker Compose доступен

echo.
echo [2/8] Проверка статуса сервисов...
docker-compose ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Сервисы не запущены!
    echo Запустите: docker-compose up -d
    pause
    exit /b 1
)
echo ✓ Сервисы запущены

echo.
echo [3/8] Проверка backend API...
echo Проверка health endpoint...
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend API недоступен
    echo Проверьте логи: docker-compose logs backend
) else (
    echo ✓ Backend API доступен
)

echo.
echo [4/8] Проверка frontend...
echo Проверка frontend...
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend недоступен
    echo Проверьте логи: docker-compose logs frontend
) else (
    echo ✓ Frontend доступен
)

echo.
echo [5/8] Проверка базы данных...
echo Проверка подключения к PostgreSQL...
docker-compose exec database pg_isready -U paygo_user >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: База данных недоступна
    echo Проверьте логи: docker-compose logs database
) else (
    echo ✓ База данных доступна
)

echo.
echo [6/8] Проверка Redis...
echo Проверка подключения к Redis...
docker-compose exec redis redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Redis недоступен
    echo Проверьте логи: docker-compose logs redis
) else (
    echo ✓ Redis доступен
)

echo.
echo [7/8] Проверка мониторинга...
echo Проверка Prometheus...
curl -f http://localhost:9090 >nul 2>&1
if %errorlevel% neq 0 (
    echo INFO: Prometheus не настроен (не критично)
) else (
    echo ✓ Prometheus доступен
)

echo.
echo [8/8] Проверка производительности...
echo Проверка времени отклика backend...
set start_time=%time%
curl -s http://localhost:8000/api/health >nul 2>&1
set end_time=%time%
echo ✓ Backend отклик: %start_time% - %end_time%

echo.
echo ========================================
echo РЕЗУЛЬТАТЫ ПРОВЕРКИ ЗДОРОВЬЯ
echo ========================================
echo.
echo Docker: ✓
echo Сервисы: ✓
echo Backend API: Проверено
echo Frontend: Проверено
echo База данных: Проверено
echo Redis: Проверено
echo Мониторинг: Проверено
echo Производительность: Проверено
echo.
echo Для детальной диагностики используйте:
echo - docker-compose logs [service_name]
echo - docker stats
echo - docker-compose exec [service_name] [command]
echo.
pause
