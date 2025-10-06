# Запуск PayGo без Docker

## 🚀 Быстрый запуск

### Вариант 1: Через PowerShell (рекомендуется)

1. Откройте PowerShell от имени администратора
2. Перейдите в папку проекта:
   ```powershell
   cd "C:\German\PayGo"
   ```
3. Запустите скрипт:
   ```powershell
   .\scripts\run_simple.ps1
   ```

### Вариант 2: Через командную строку (cmd)

1. Откройте командную строку (cmd)
2. Перейдите в папку проекта:
   ```cmd
   cd "C:\German\PayGo"
   ```
3. Запустите скрипт:
   ```cmd
   scripts\run_simple.bat
   ```

### Вариант 3: Ручной запуск

1. Откройте командную строку или PowerShell
2. Перейдите в папку backend:
   ```cmd
   cd PROJECT\web-service\backend
   ```
3. Установите зависимости:
   ```cmd
   pip install fastapi uvicorn[standard] pydantic
   ```
4. Запустите сервер:
   ```cmd
   python simple_main.py
   ```

## 🌐 Доступ к приложению

После успешного запуска:

- **API сервер**: http://localhost:8000
- **Документация API**: http://localhost:8000/api/docs
- **Проверка здоровья**: http://localhost:8000/api/health

## 📋 Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Доступ к интернету для установки зависимостей

## 🔧 Устранение проблем

### Python не найден
Установите Python с официального сайта: https://www.python.org/downloads/

### Ошибки с зависимостями
Попробуйте обновить pip:
```cmd
python -m pip install --upgrade pip
```

### Порт 8000 занят
Измените порт в файле `simple_main.py` или освободите порт 8000

## 📱 Тестирование API

Откройте браузер и перейдите по адресу:
http://localhost:8000/api/docs

Там вы сможете протестировать все доступные эндпоинты.

## 🛑 Остановка сервера

Нажмите `Ctrl+C` в терминале, где запущен сервер.
