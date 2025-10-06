@echo off
echo ========================================
echo PayGo - ИСПРАВЛЕНИЕ И ЗАПУСК
echo ========================================
echo.

echo [1] Проверяем структуру проекта...
if not exist "PROJECT" (
    echo ❌ Папка PROJECT не найдена!
    pause
    exit /b 1
)

if not exist "web-service" (
    echo ❌ Папка web-service не найдена!
    pause
    exit /b 1
)

echo ✓ Структура проверена

echo [2] Перенос web-service в PROJECT...
move "web-service" "PROJECT\"
if errorlevel 1 (
    echo ❌ Ошибка переноса web-service!
    pause
    exit /b 1
)
echo ✓ web-service перенесен в PROJECT

echo [3] Перенос tests в PROJECT...
if exist "tests" (
    move "tests" "PROJECT\"
    echo ✓ tests перенесен в PROJECT
)

echo [4] Переход в папку PROJECT...
cd PROJECT
if errorlevel 1 (
    echo ❌ Ошибка перехода в PROJECT!
    pause
    exit /b 1
)
echo ✓ Перешли в папку PROJECT

echo [5] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Docker не установлен или не запущен!
    echo Запустите Docker Desktop и попробуйте снова.
    pause
    exit /b 1
)
echo ✓ Docker доступен

echo [6] Проверка docker-compose.yml...
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml не найден!
    pause
    exit /b 1
)
echo ✓ docker-compose.yml найден

echo [7] Сборка и запуск проекта...
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
echo Запускаем сервисы...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Ошибка запуска!
    echo Проверьте логи выше.
    pause
    exit /b 1
)

echo.
echo [8] Ожидание запуска сервисов...
echo Ждем 30 секунд для полного запуска...
timeout /t 30 /nobreak >nul

echo [9] Проверка статуса сервисов...
docker-compose ps

echo.
echo [10] Проверка доступности сервисов...
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
