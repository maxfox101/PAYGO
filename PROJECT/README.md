# PayGo - Система платежных терминалов

PayGo - это современная система управления платежными терминалами с веб-интерфейсом, API и мобильными приложениями.

## 🚀 Возможности

- **Платежные терминалы**: Управление и мониторинг терминалов
- **Пользователи**: Регистрация, аутентификация, профили
- **Карты**: Безопасное хранение и управление платежными картами
- **Транзакции**: Отслеживание всех платежных операций
- **Аналитика**: Детальная отчетность и статистика
- **Безопасность**: Двухфакторная аутентификация, шифрование данных
- **API**: RESTful API для интеграции с внешними системами
- **Правовые документы**: Оферта, условия использования, политика конфиденциальности

## 🏗️ Архитектура

```
PayGo/
├── web-service/         # Веб-сервис
│   ├── backend/         # FastAPI backend
│   ├── frontend/        # React frontend
│   ├── database/        # База данных PostgreSQL
│   └── api/             # API компоненты
├── terminal/            # Терминальное приложение
├── config/              # Конфигурационные файлы
├── docs/                # Документация
│   └── LEGAL_DOCUMENTS.md # Система правовых документов
├── scripts/             # Скрипты развертывания
├── .github/             # CI/CD конфигурации
└── docker-compose.yml   # Docker конфигурация
```

## 🛠️ Технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - основная база данных
- **Redis** - кеширование и сессии
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных
- **JWT** - аутентификация

### Frontend
- **React** - пользовательский интерфейс
- **Ant Design** - UI компоненты
- **Redux Toolkit** - управление состоянием
- **React Router** - навигация
- **Axios** - HTTP клиент

### DevOps & Мониторинг
- **Docker** - контейнеризация
- **Prometheus** - метрики и мониторинг
- **Grafana** - визуализация данных
- **GitHub Actions** - CI/CD
- **Nginx** - веб-сервер и прокси

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 20GB свободного места
- Linux/macOS/Windows

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/paygo.git
cd paygo
```

### 2. Настройка окружения

```bash
# Копирование конфигурации (если есть)
cp .env.example .env

# Редактирование переменных окружения
nano .env
```

Основные переменные окружения:
```env
# База данных
DATABASE_URL=postgresql://user:password@localhost/paygo
POSTGRES_USER=paygo
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=paygo

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# API
API_V1_STR=/api/v1
PROJECT_NAME=PayGo
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Безопасность
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 4. Инициализация базы данных

```bash
# Создание таблиц и индексов
docker-compose exec backend python -m alembic upgrade head

# Создание тестовых данных (опционально)
docker-compose exec backend python scripts/create_test_data.py
```

### 5. Доступ к приложению

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

## 🔧 Детальная настройка

### Настройка Redis кеширования

Redis автоматически настроен для:
- Кеширования сессий пользователей
- Кеширования часто запрашиваемых данных
- Хранения временных данных

```python
from cache.redis_cache import redis_cache

# Кеширование данных
await redis_cache.set_data("user:123", user_data, ttl=3600)

# Получение данных
user_data = await redis_cache.get_data("user:123")
```

### Настройка Connection Pooling

PostgreSQL connection pool автоматически оптимизирован:
- Размер пула: 20 соединений
- Максимальный overflow: 30 соединений
- Автоматическая очистка недействительных соединений

```python
from database.connection_pool import get_db_session

async with get_db_session() as session:
    # Работа с базой данных
    result = await session.execute(query)
```

### Оптимизация базы данных

База данных предварительно настроена с:
- Оптимизированными индексами для всех таблиц
- Частичными индексами для активных записей
- Геопространственными индексами для локаций
- Материализованными представлениями для статистики

### Lazy Loading для React

Frontend использует lazy loading для оптимизации:
- Автоматическая загрузка компонентов по требованию
- Предзагрузка критически важных страниц
- Error boundaries для обработки ошибок

```javascript
import { LazyDashboard, LazyCards } from './components/LazyComponents';

// Компоненты загружаются автоматически
<Route path="/dashboard" element={<LazyDashboard />} />
<Route path="/cards" element={<LazyCards />} />
```

## 📊 Мониторинг и метрики

### Prometheus метрики

Система автоматически собирает:
- HTTP запросы и ответы
- Время выполнения запросов
- Использование памяти и CPU
- Статистика базы данных
- Статистика Redis

### Grafana дашборды

Предустановленные дашборды:
- Общая производительность системы
- Мониторинг API endpoints
- Статистика базы данных
- Мониторинг Redis
- Системные ресурсы

### Алерты

Автоматические уведомления при:
- Высокой нагрузке на API
- Медленных запросах
- Проблемах с базой данных
- Высоком использовании ресурсов

## 🧪 Тестирование

### Запуск тестов

```bash
# Backend тесты
cd web-service/backend
pytest tests/ -v --cov=. --cov-report=html

# Frontend тесты
cd web-service/frontend
npm test

# Тесты производительности
pytest tests/test_performance.py -v --benchmark-only
```

### Покрытие кода

Требования к покрытию:
- Backend: минимум 80%
- Frontend: минимум 70%
- Критические компоненты: минимум 90%

## 🔒 Безопасность

### Аутентификация и авторизация

- JWT токены с коротким временем жизни
- Refresh токены для обновления сессий
- Двухфакторная аутентификация (TOTP)
- Роли и разрешения пользователей

### Защита данных

- Шифрование паролей (bcrypt)
- Хеширование номеров карт
- HTTPS для всех соединений
- Валидация входных данных

### Аудит и логирование

- Логирование всех действий пользователей
- Отслеживание изменений в данных
- Мониторинг подозрительной активности
- Резервное копирование данных

## 🚀 Развертывание в продакшене

### Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Настройка продакшена

```bash
# Копирование продакшен конфигурации
cp docker-compose.prod.yml docker-compose.yml
cp .env.prod .env

# Настройка переменных окружения
nano .env

# Запуск в продакшене
docker-compose -f docker-compose.prod.yml up -d
```

### SSL сертификаты

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличение количества backend инстансов
docker-compose up -d --scale backend=3

# Балансировка нагрузки с Nginx
docker-compose up -d nginx
```

### Вертикальное масштабирование

```bash
# Увеличение ресурсов в docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

### Кластерное развертывание

Для высоконагруженных систем рекомендуется:
- Kubernetes для оркестрации
- Redis Cluster для кеширования
- PostgreSQL репликация
- Load balancer для распределения нагрузки

## 🐛 Устранение неполадок

### Частые проблемы

1. **База данных не подключается**
   ```bash
   docker-compose logs database
   docker-compose exec database psql -U paygo -d paygo
   ```

2. **Redis недоступен**
   ```bash
   docker-compose logs redis
   docker-compose exec redis redis-cli ping
   ```

3. **Frontend не загружается**
   ```bash
   docker-compose logs frontend
   docker-compose exec frontend nginx -t
   ```

### Логи и отладка

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Вход в контейнер для отладки
docker-compose exec backend bash
```

## 📚 Документация

- [API документация](docs/API_DOCUMENTATION.md)
- [Руководство разработчика](docs/DEVELOPMENT.md)
- [Настройка NGROK](docs/NGROK_SETUP.md)
- [Docker настройка](DOCKER_SETUP.md)
- [Отчет об очистке](docs/CLEANUP_REPORT.md)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создание feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создание Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/your-username/paygo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/paygo/discussions)
- **Email**: support@paygo.com

## 🙏 Благодарности

- FastAPI сообществу за отличный фреймворк
- React команде за инновационный подход к UI
- Docker сообществу за контейнеризацию
- Всем контрибьюторам проекта

---

**PayGo** - Современные платежные решения для современного мира 💳✨ 