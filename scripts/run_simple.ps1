Write-Host "========================================" -ForegroundColor Green
Write-Host "PayGo - ЗАПУСК ПРОСТОЙ ВЕРСИИ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "[1] Переход в папку backend..." -ForegroundColor Yellow
Set-Location "PROJECT\web-service\backend"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка: папка backend не найдена!" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "✓ Перешли в папку backend" -ForegroundColor Green

Write-Host "[2] Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python доступен: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка: Python не установлен!" -ForegroundColor Red
    Write-Host "Установите Python 3.8+ и попробуйте снова." -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[3] Установка зависимостей..." -ForegroundColor Yellow
Write-Host "Устанавливаем необходимые пакеты..." -ForegroundColor Cyan
try {
    pip install fastapi uvicorn[standard] pydantic
    Write-Host "✓ Зависимости установлены" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Предупреждение: не удалось установить все зависимости" -ForegroundColor Yellow
    Write-Host "Продолжаем запуск..." -ForegroundColor Cyan
}

Write-Host "[4] Запуск простого API сервера..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Запускаем PayGo API..." -ForegroundColor Green
Write-Host "📍 Адрес: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Документация: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "💓 Здоровье: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Нажмите Ctrl+C для остановки сервера" -ForegroundColor Yellow
Write-Host ""

python simple_main.py

Read-Host "Нажмите Enter для выхода"



