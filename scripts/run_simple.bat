@echo off
echo ========================================
echo PayGo - ЗАПУСК ПРОСТОЙ ВЕРСИИ
echo ========================================
echo.

echo [1] Переход в папку backend...
cd PROJECT\web-service\backend
if errorlevel 1 (
    echo ❌ Ошибка: папка backend не найдена!
    pause
    exit /b 1
)
echo ✓ Перешли в папку backend

echo [2] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ошибка: Python не установлен!
    echo Установите Python 3.8+ и попробуйте снова.
    pause
    exit /b 1
)
echo ✓ Python доступен

echo [3] Установка зависимостей...
echo Устанавливаем необходимые пакеты...
pip install fastapi uvicorn[standard] pydantic
if errorlevel 1 (
    echo ⚠️ Предупреждение: не удалось установить все зависимости
    echo Продолжаем запуск...
)

echo [4] Запуск простого API сервера...
echo.
echo 🚀 Запускаем PayGo API...
echo 📍 Адрес: http://localhost:8000
echo 📚 Документация: http://localhost:8000/api/docs
echo 💓 Здоровье: http://localhost:8000/api/health
echo.
echo Нажмите Ctrl+C для остановки сервера
echo.

python simple_main.py

pause



