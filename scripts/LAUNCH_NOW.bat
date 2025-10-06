@echo off
echo ========================================
echo PayGo - ЗАПУСК ПРОЕКТА
echo ========================================
echo.

echo [1] Переход в папку PROJECT...
cd PROJECT
if errorlevel 1 (
    echo ❌ Ошибка перехода в PROJECT!
    pause
    exit /b 1
)
echo ✓ Перешли в папку PROJECT

echo [2] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не доступен!
    echo Запустите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)
echo ✓ Docker доступен

echo [3] Проверка docker-compose.yml...
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml не найден!
    pause
    exit /b 1
)
echo ✓ docker-compose.yml найден

echo [4] Сборка проекта...
echo.
echo Собираем Docker образы...
docker-compose build
if errorlevel 1 (
    echo ❌ Ошибка сборки!
    echo Проверьте логи выше.
    pause
    exit /b 1
)

echo.
echo [5] Запуск сервисов...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Ошибка запуска!
    echo Проверьте логи выше.
    pause
    exit /b 1
)

echo.
echo [6] Ожидание запуска сервисов...
echo Ждем 45 секунд для полного запуска...
timeout /t 45 /nobreak >nul

echo [7] Проверка статуса сервисов...
docker-compose ps

echo.
echo [8] Проверка доступности сервисов...
echo.
echo Проверяем backend API...
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend API еще не готов
) else (
    echo ✅ Backend API доступен: http://localhost:8000
)

echo.
echo Проверяем frontend...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Frontend еще не готов
) else (
    echo ✅ Frontend доступен: http://localhost:3000
)

echo.
echo ========================================
echo ПРОЕКТ ЗАПУЩЕН!
echo ========================================
echo.
echo 🌐 Сайт: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo 📊 Prometheus: http://localhost:9090
echo.
echo 💡 Если страница все еще недоступна:
echo    1. Подождите еще 1-2 минуты
echo    2. Проверьте логи: docker-compose logs -f
echo    3. Убедитесь, что порты 3000 и 8000 свободны
echo.
echo Нажмите любую клавишу для просмотра логов...
pause >nul

echo.
echo Показываем логи всех сервисов...
docker-compose logs -f
