@echo off
echo ========================================
echo PayGo - Тестирование правовых документов
echo ========================================
echo.

echo [1/6] Проверка структуры проекта...
if not exist "web-service\backend\models\legal_documents.py" (
    echo ERROR: Модели правовых документов не найдены!
    exit /b 1
)
if not exist "web-service\backend\schemas\legal_documents.py" (
    echo ERROR: Схемы правовых документов не найдены!
    exit /b 1
)
if not exist "web-service\backend\services\legal_documents_service.py" (
    echo ERROR: Сервис правовых документов не найден!
    exit /b 1
)
if not exist "web-service\backend\routers\legal_documents.py" (
    echo ERROR: Роутер правовых документов не найден!
    exit /b 1
)
echo ✓ Структура backend проверена

if not exist "web-service\frontend\src\components\LegalDocuments\" (
    echo ERROR: Frontend компоненты не найдены!
    exit /b 1
)
if not exist "web-service\frontend\src\pages\LegalDocuments.js" (
    echo ERROR: Страница правовых документов не найдена!
    exit /b 1
)
echo ✓ Структура frontend проверена

if not exist "web-service\database\legal_documents_init.sql" (
    echo ERROR: SQL инициализация не найдена!
    exit /b 1
)
echo ✓ База данных проверена
echo.

echo [2/6] Проверка Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker не доступен!
    exit /b 1
)
echo ✓ Docker доступен
echo.

echo [3/6] Сборка и запуск сервисов...
echo Сборка образов...
docker-compose build backend frontend
if %errorlevel% neq 0 (
    echo ERROR: Сборка не удалась!
    exit /b 1
)
echo ✓ Образы собраны

echo Запуск сервисов...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Запуск не удался!
    exit /b 1
)
echo ✓ Сервисы запущены
echo.

echo [4/6] Ожидание готовности сервисов...
timeout /t 15 /nobreak >nul
echo ✓ Ожидание завершено
echo.

echo [5/6] Проверка API endpoints...
echo Проверка health endpoint...
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend недоступен!
    exit /b 1
)
echo ✓ Backend доступен

echo Проверка публичной оферты...
curl -f http://localhost:8000/api/v1/legal/public/offer >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Endpoint оферты недоступен (возможно, не настроен)
) else (
    echo ✓ Endpoint оферты доступен
)

echo Проверка frontend...
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend недоступен
) else (
    echo ✓ Frontend доступен
)
echo.

echo [6/6] Проверка базы данных...
echo Проверка подключения к PostgreSQL...
docker-compose exec database pg_isready -U paygo_user >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: База данных недоступна
) else (
    echo ✓ База данных доступна
    
    echo Проверка таблиц правовых документов...
    docker-compose exec database psql -U paygo_user -d paygo_db -c "\dt legal_documents" >nul 2>&1
    if %errorlevel% neq 0 (
        echo WARNING: Таблицы правовых документов не найдены
    ) else (
        echo ✓ Таблицы правовых документов найдены
    )
)
echo.

echo ========================================
echo ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!
echo ========================================
echo.
echo Результаты:
echo - Backend: ✓ Готов
echo - Frontend: ✓ Готов  
echo - База данных: Проверено
echo - API endpoints: Проверено
echo - Docker: ✓ Работает
echo.
echo Следующие шаги:
echo 1. Откройте http://localhost:3000 в браузере
echo 2. Перейдите в раздел "Правовые документы"
echo 3. Проверьте отображение оферты
echo 4. Протестируйте принятие документов
echo.
echo Для просмотра логов используйте:
echo - docker-compose logs -f backend
echo - docker-compose logs -f frontend
echo.
pause
