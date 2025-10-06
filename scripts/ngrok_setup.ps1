# PayGo Ngrok Setup Script
Write-Host "🚀 PayGo Ngrok Setup" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green

Write-Host ""
Write-Host "📥 Скачайте Ngrok с https://ngrok.com/" -ForegroundColor Yellow
Write-Host "📁 Распакуйте в C:\ngrok" -ForegroundColor Yellow
Write-Host "🔑 Зарегистрируйтесь и получите authtoken" -ForegroundColor Yellow

Write-Host ""
Write-Host "💡 После установки выполните:" -ForegroundColor Cyan
Write-Host "ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor White

Write-Host ""
Write-Host "🌐 Для запуска туннелей:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API (порт 8000):" -ForegroundColor Yellow
Write-Host "ngrok http 8000" -ForegroundColor White
Write-Host ""
Write-Host "Frontend (порт 8080):" -ForegroundColor Yellow
Write-Host "ngrok http 8080" -ForegroundColor White

Write-Host ""
Write-Host "⚠️  ВАЖНО: Замените YOUR_TOKEN на ваш реальный токен!" -ForegroundColor Red
Write-Host ""
Read-Host "Нажмите Enter для продолжения"

