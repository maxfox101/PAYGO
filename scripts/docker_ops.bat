@echo off
echo ========================================
echo PayGo - Docker операции
echo ========================================
echo.

:menu
echo Выберите операцию:
echo 1. Сборка образов (docker-compose build)
echo 2. Запуск сервисов (docker-compose up -d)
echo 3. Проверка статуса (docker-compose ps)
echo 4. Просмотр логов backend
echo 5. Просмотр логов frontend
echo 6. Просмотр логов database
echo 7. Просмотр логов redis
echo 8. Остановка сервисов (docker-compose down)
echo 9. Перезапуск сервисов
echo 0. Выход
echo.
set /p choice="Введите номер (0-9): "

if "%choice%"=="1" goto build
if "%choice%"=="2" goto up
if "%choice%"=="3" goto ps
if "%choice%"=="4" goto logs_backend
if "%choice%"=="5" goto logs_frontend
if "%choice%"=="6" goto logs_database
if "%choice%"=="7" goto logs_redis
if "%choice%"=="8" goto down
if "%choice%"=="9" goto restart
if "%choice%"=="0" goto exit
echo Неверный выбор. Попробуйте снова.
echo.
goto menu

:build
echo.
echo [1/1] Сборка Docker образов...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Сборка не удалась!
    pause
    goto menu
)
echo ✓ Образы собраны успешно
pause
goto menu

:up
echo.
echo [1/1] Запуск сервисов...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Запуск не удался!
    pause
    goto menu
)
echo ✓ Сервисы запущены
echo.
echo Ожидание готовности сервисов...
timeout /t 10 /nobreak >nul
echo.
echo Проверка статуса:
docker-compose ps
pause
goto menu

:ps
echo.
echo Статус сервисов:
docker-compose ps
echo.
echo Использование ресурсов:
docker stats --no-stream
pause
goto menu

:logs_backend
echo.
echo Логи backend (Ctrl+C для выхода):
docker-compose logs -f backend
goto menu

:logs_frontend
echo.
echo Логи frontend (Ctrl+C для выхода):
docker-compose logs -f frontend
goto menu

:logs_database
echo.
echo Логи database (Ctrl+C для выхода):
docker-compose logs -f database
goto menu

:logs_redis
echo.
echo Логи redis (Ctrl+C для выхода):
docker-compose logs -f redis
goto menu

:down
echo.
echo [1/1] Остановка сервисов...
docker-compose down
if %errorlevel% neq 0 (
    echo ERROR: Остановка не удалась!
    pause
    goto menu
)
echo ✓ Сервисы остановлены
pause
goto menu

:restart
echo.
echo [1/2] Остановка сервисов...
docker-compose down
echo [2/2] Запуск сервисов...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Перезапуск не удался!
    pause
    goto menu
)
echo ✓ Сервисы перезапущены
pause
goto menu

:exit
echo.
echo До свидания!
exit /b 0
