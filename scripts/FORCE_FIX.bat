@echo off
echo ========================================
echo PayGo - ПРИНУДИТЕЛЬНОЕ ИСПРАВЛЕНИЕ
echo ========================================
echo.

echo [1] Проверяем права администратора...
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ Запустите cmd.exe от имени администратора!
    echo Нажмите Win+X и выберите "Командная строка (Администратор)"
    pause
    exit /b 1
)
echo ✓ Права администратора получены

echo [2] Остановка всех Docker процессов...
docker stop $(docker ps -q) >nul 2>&1
echo ✓ Docker процессы остановлены

echo [3] Принудительное удаление web-service из PROJECT (если есть)...
if exist "PROJECT\web-service" (
    rmdir /s /q "PROJECT\web-service"
    echo ✓ Старый web-service удален
)

echo [4] Копирование web-service в PROJECT...
xcopy "web-service" "PROJECT\web-service\" /E /I /H /Y
if errorlevel 1 (
    echo ❌ Ошибка копирования!
    pause
    exit /b 1
)
echo ✓ web-service скопирован в PROJECT

echo [5] Копирование tests в PROJECT...
if exist "tests" (
    xcopy "tests" "PROJECT\tests\" /E /I /H /Y
    echo ✓ tests скопирован в PROJECT
)

echo [6] Переход в папку PROJECT...
cd PROJECT
if errorlevel 1 (
    echo ❌ Ошибка перехода в PROJECT!
    pause
    exit /b 1
)
echo ✓ Перешли в папку PROJECT

echo [7] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не доступен!
    pause
    exit /b 1
)
echo ✓ Docker доступен

echo [8] Сборка проекта...
docker-compose build
if errorlevel 1 (
    echo ❌ Ошибка сборки!
    pause
    exit /b 1
)

echo [9] Запуск сервисов...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Ошибка запуска!
    pause
    exit /b 1
)

echo [10] Ожидание запуска (60 секунд)...
timeout /t 60 /nobreak >nul

echo [11] Проверка статуса...
docker-compose ps

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






