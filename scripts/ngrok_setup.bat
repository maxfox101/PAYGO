@echo off
echo 🚀 PayGo Ngrok Setup
echo ====================

echo.
echo 📥 Скачайте Ngrok с https://ngrok.com/
echo 📁 Распакуйте в C:\ngrok
echo 🔑 Зарегистрируйтесь и получите authtoken
echo.

echo 💡 После установки выполните:
echo ngrok config add-authtoken YOUR_TOKEN
echo.

echo 🌐 Для запуска туннелей:
echo.
echo Backend API (порт 8000):
echo ngrok http 8000
echo.
echo Frontend (порт 8080):
echo ngrok http 8080
echo.

echo ⚠️  ВАЖНО: Замените YOUR_TOKEN на ваш реальный токен!
echo.
pause

