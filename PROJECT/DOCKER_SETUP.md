# 🐳 Docker Setup для PayGo

## 📋 Предварительные требования

### 1. Установка Docker
- **Windows**: Скачайте и установите [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **macOS**: Скачайте и установите [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Выполните команды:
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  ```

### 2. Установка Docker Compose
- **Windows/macOS**: Входит в Docker Desktop
- **Linux**: Выполните команды:
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```

### 3. Проверка установки
```bash
docker --version
docker-compose --version
```

## 🚀 Пошаговый запуск проекта

### Шаг 1: Клонирование репозитория
```bash
git clone <your-repo-url>
cd PayGo
```

### Шаг 2: Создание файла .env
```bash
# Создайте файл .env в корне проекта
cp .env.example .env
# Отредактируйте .env файл под ваши настройки
```

### Шаг 3: Сборка образов
```bash
# Собрать все Docker образы
docker-compose build

# Или собрать конкретный сервис
docker-compose build backend
docker-compose build frontend
```

### Шаг 4: Запуск сервисов
```bash
# Запустить все сервисы в фоновом режиме
docker-compose up -d

# Или запустить с выводом логов
docker-compose up
```

### Шаг 5: Проверка статуса
```bash
# Проверить статус всех сервисов
docker-compose ps

# Посмотреть логи
docker-compose logs -f
```

## 🌐 Доступ к сервисам

После успешного запуска:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://localhost:3000 | Веб-интерфейс |
| **Backend API** | http://localhost:8000 | REST API |
| **API Документация** | http://localhost:8000/api/docs | Swagger UI |
| **База данных** | localhost:5432 | PostgreSQL |
| **Redis** | localhost:6379 | Кэш и сессии |

## 🛠️ Управление Docker

### Основные команды
```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes
docker-compose down -v

# Перезапустить сервис
docker-compose restart backend

# Обновить и перезапустить
docker-compose up -d --build

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Информация о контейнерах
docker ps -a

# Информация об образах
docker images
```

## 🔧 Устранение неполадок

### Проблема: Порт уже занят
```bash
# Найти процесс, использующий порт
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS

# Остановить процесс или изменить порт в docker-compose.yml
```

### Проблема: Ошибки сборки
```bash
# Очистить кэш Docker
docker system prune -a

# Пересобрать образ
docker-compose build --no-cache
```

### Проблема: База данных не подключается
```bash
# Проверить статус БД
docker-compose logs database

# Перезапустить БД
docker-compose restart database

# Проверить переменные окружения
docker-compose exec backend env | grep DATABASE
```

### Проблема: Недостаточно места на диске
```bash
# Очистить неиспользуемые образы и контейнеры
docker system prune -a

# Очистить volumes
docker volume prune
```

## 📁 Структура Docker

```
PayGo/
├── docker-compose.yml          # Основной файл конфигурации
├── .env                        # Переменные окружения
├── web-service/
│   ├── backend/
│   │   ├── Dockerfile         # Образ для backend
│   │   └── requirements.txt   # Python зависимости
│   └── frontend/
│       ├── Dockerfile         # Образ для frontend
│       └── nginx.conf         # Конфигурация Nginx
└── config/
    ├── nginx.conf             # Основной Nginx
    └── prometheus.yml         # Мониторинг
```

## 🔒 Безопасность

### Переменные окружения
```bash
# Обязательно измените в продакшене:
SECRET_KEY=your-super-secret-key-change-in-production
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-secure-redis-password
```

### Сетевые настройки
- Все сервисы работают в изолированной сети `paygo_network`
- Внешние порты открыты только для необходимых сервисов
- База данных доступна только внутри Docker сети

## 📊 Мониторинг и логи

### Логи
```bash
# Все логи
docker-compose logs

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database

# Логи в реальном времени
docker-compose logs -f
```

### Метрики
- Prometheus доступен на порту 9090 (если настроен)
- Grafana доступен на порту 3001 (если настроен)

## 🚀 Продакшн настройки

### Оптимизация
```bash
# Использовать production образы
docker-compose -f docker-compose.prod.yml up -d

# Настроить volumes для данных
docker volume create paygo_postgres_data
docker volume create paygo_redis_data
```

### Масштабирование
```bash
# Запустить несколько экземпляров backend
docker-compose up -d --scale backend=3

# Настроить балансировщик нагрузки
docker-compose up -d nginx
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что все порты свободны
3. Проверьте версии Docker и Docker Compose
4. Очистите кэш: `docker system prune -a`

## 🔄 Обновление

```bash
# Получить последние изменения
git pull

# Пересобрать и перезапустить
docker-compose down
docker-compose up -d --build
```

---

**PayGo** © 2025. Сделано с ❤️ для цифровизации платежей в России.

