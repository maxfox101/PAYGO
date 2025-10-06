@echo off
echo ========================================
echo PayGo - ДИАГНОСТИКА ПРОБЛЕМ
echo ========================================
echo.

echo [1] Проверка текущей папки...
echo Текущая папка: %CD%
echo.

echo [2] Проверка структуры проекта...
if exist "PROJECT" (
    echo ✓ Папка PROJECT найдена
    if exist "PROJECT\web-service" (
        echo ✓ web-service в PROJECT найден
    ) else (
        echo ❌ web-service в PROJECT НЕ найден!
    )
    if exist "PROJECT\docker-compose.yml" (
        echo ✓ docker-compose.yml в PROJECT найден
    ) else (
        echo ❌ docker-compose.yml в PROJECT НЕ найден!
    )
) else (
    echo ❌ Папка PROJECT НЕ найдена!
)
echo.

echo [3] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker НЕ доступен!
    echo Запустите Docker Desktop
) else (
    echo ✓ Docker доступен
    docker --version
)
echo.

echo [4] Проверка запущенных контейнеров...
docker ps
echo.

echo [5] Проверка портов...
echo Проверяем порт 3000 (frontend)...
netstat -an | findstr :3000
echo.
echo Проверяем порт 8000 (backend)...
netstat -an | findstr :8000
echo.

echo [6] Проверка файлов в PROJECT...
if exist "PROJECT" (
    echo Содержимое PROJECT:
    dir PROJECT
) else (
    echo Папка PROJECT не найдена!
)
echo.

echo [7] Проверка docker-compose.yml...
if exist "PROJECT\docker-compose.yml" (
    echo Содержимое docker-compose.yml:
    type "PROJECT\docker-compose.yml"
) else (
    echo docker-compose.yml не найден!
)
echo.

echo ========================================
echo ДИАГНОСТИКА ЗАВЕРШЕНА
echo ========================================
echo.
echo Нажмите любую клавишу для продолжения...
pause >nul

echo.
echo [8] Попытка запуска проекта...
cd PROJECT
if errorlevel 1 (
    echo ❌ Не удалось перейти в PROJECT!
    pause
    exit /b 1
)

echo ✓ Перешли в PROJECT
echo.
echo Собираем проект...
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
echo Ждем 30 секунд...
timeout /t 30 /nobreak >nul

echo.
echo Проверяем статус...
docker-compose ps

echo.
echo Проверяем доступность...
curl -s http://localhost:8000/api/health
echo.
curl -s http://localhost:3000
echo.

echo.
echo ========================================
echo ПРОЕКТ ЗАПУЩЕН!
echo ========================================
echo.
echo 🌐 Сайт: http://localhost:3000
echo 🔧 API: http://localhost:8000
echo.
echo Нажмите любую клавишу для просмотра логов...
pause >nul

docker-compose logs -f





