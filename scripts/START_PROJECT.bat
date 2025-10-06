@echo off
echo ========================================
echo PayGo - ЗАПУСК ПРОЕКТА
echo ========================================
echo.

echo [1] Переход в папку PROJECT...
cd PROJECT
if errorlevel 1 (
    echo ❌ Ошибка: папка PROJECT не найдена!
    echo Убедитесь, что реорганизация завершена.
    pause
    exit /b 1
)
echo ✓ Перешли в папку PROJECT

echo [2] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Docker не установлен или не запущен!
    echo Запустите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)
echo ✓ Docker доступен

echo [3] Сборка и запуск проекта...
echo.
echo Собираем Docker образы...
docker-compose build
if errorlevel 1 (
    echo ❌ Ошибка сборки!
    pause
    exit /b 1
)

echo.
echo Запускаем сервисы...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Ошибка запуска!
    pause
    exit /b 1
)

echo.
echo [4] Проверка статуса сервисов...
timeout /t 5 /nobreak >nul
docker-compose ps

echo.
echo [5] Проверка доступности сервисов...
echo.
echo Проверяем backend API...
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend API еще не готов, подождите немного...
) else (
    echo ✅ Backend API доступен: http://localhost:8000
)

echo.
echo Проверяем frontend...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Frontend еще не готов, подождите немного...
) else (
    echo ✅ Frontend доступен: http://localhost:3000
)

echo.
echo Проверяем Prometheus...
curl -s http://localhost:9090 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Prometheus еще не готов, подождите немного...
) else (
    echo ✅ Prometheus доступен: http://localhost:9090
)

echo.
echo ========================================
echo ПРОЕКТ ЗАПУЩЕН!
echo ========================================
echo.
echo 🌐 Сайт: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo 📊 Мониторинг: http://localhost:9090
echo.
echo 💡 Если сервисы не готовы, подождите 1-2 минуты
echo 💡 Для просмотра логов: docker-compose logs -f
echo.
echo Нажмите любую клавишу для просмотра логов...
pause >nul

echo.
echo Показываем логи backend...
docker-compose logs -f backend
