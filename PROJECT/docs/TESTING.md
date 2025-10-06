# PayGo - Руководство по тестированию

## 📋 Обзор

Этот документ описывает комплексную стратегию тестирования системы PayGo, включая unit тесты, интеграционные тесты, тесты производительности и ручные проверки.

## 🚀 Быстрый старт

### 1. Автоматическая проверка
```bash
# Запуск всех проверок
scripts\test_all.bat

# Запуск всех тестов
scripts\run_tests.bat

# Проверка здоровья системы
scripts\health_check.bat
```

### 2. Docker операции
```bash
# Интерактивное меню Docker операций
scripts\docker_ops.bat
```

## 🧪 Типы тестов

### Unit тесты
- **Backend**: Python + pytest
- **Frontend**: React + Jest
- **Покрытие**: Минимум 80%

### Интеграционные тесты
- **API endpoints**: Тестирование полного цикла
- **Database**: Проверка CRUD операций
- **Cache**: Redis интеграция
- **Auth**: Аутентификация и авторизация

### Тесты производительности
- **Redis**: Latency, throughput, memory
- **Database**: Connection pool, query performance
- **API**: Response time, concurrent users
- **Load testing**: Stress testing с Locust

### E2E тесты
- **User flows**: Полные пользовательские сценарии
- **Cross-browser**: Chrome, Firefox, Safari
- **Mobile**: Responsive design testing

## 🔧 Настройка окружения

### Требования
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Переменные окружения
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/paygo
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
DEBUG=False

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

## 📊 Запуск тестов

### Backend тесты
```bash
cd web-service/backend

# Все тесты
pytest tests/ -v --cov=. --cov-report=html

# Только performance тесты
pytest tests/test_performance.py -v

# Только integration тесты
pytest tests/ -m integration -v

# Параллельное выполнение
pytest tests/ -n auto --dist=loadfile
```

### Frontend тесты
```bash
cd web-service/frontend

# Unit тесты
npm test

# Coverage
npm test -- --coverage --watchAll=false

# E2E тесты (если настроены)
npm run test:e2e
```

### Performance тесты
```bash
cd web-service/backend

# Redis performance
pytest tests/test_performance.py::TestRedisCachePerformance -v

# Database performance
pytest tests/test_performance.py::TestConnectionPoolPerformance -v

# Integration performance
pytest tests/test_performance.py::TestPerformanceIntegration -v
```

## 🐳 Docker тестирование

### Сборка и запуск
```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
docker-compose logs -f redis
```

### Health checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:3000

# Database health
docker-compose exec database pg_isready -U paygo_user

# Redis health
docker-compose exec redis redis-cli ping
```

## 📈 Мониторинг и метрики

### Prometheus метрики
- **Backend**: `/metrics` endpoint
- **Redis**: Redis exporter
- **PostgreSQL**: PostgreSQL exporter
- **Nginx**: Nginx exporter
- **System**: Node exporter

### Grafana дашборды
- **API Performance**: Response time, error rate
- **Database**: Connection pool, query performance
- **Cache**: Hit rate, memory usage
- **System**: CPU, RAM, disk usage

### Алерты
- **High Error Rate**: >10% ошибок за 5 минут
- **High Response Time**: >2s среднее время ответа
- **Service Down**: Redis, PostgreSQL недоступны
- **Resource Usage**: CPU >80%, RAM >90%

## 🔒 Тестирование безопасности

### Статические анализаторы
```bash
# Python security
bandit -r web-service/backend/

# Node.js security
npm audit

# Container security
trivy image paygo-backend:latest
```

### Penetration testing
- **SQL Injection**: Тестирование всех input полей
- **XSS**: Проверка user-generated content
- **CSRF**: Тестирование форм
- **Authentication**: Brute force, session hijacking

## 📝 Ручное тестирование

### Основные сценарии
1. **Регистрация и авторизация**
   - Регистрация нового пользователя
   - Вход в систему
   - 2FA настройка и проверка
   - Восстановление пароля

2. **Управление картами**
   - Добавление новой карты
   - Редактирование карты
   - Удаление карты
   - Установка карты по умолчанию

3. **Транзакции**
   - Создание платежа
   - Обработка транзакции
   - История транзакций
   - Экспорт отчетов

4. **Терминалы**
   - Добавление терминала
   - Мониторинг статуса
   - Геолокация
   - Обновление firmware

### UI/UX проверки
- **Responsive design**: Mobile, tablet, desktop
- **Accessibility**: WCAG 2.1 AA compliance
- **Cross-browser**: Chrome, Firefox, Safari
- **Performance**: Page load time <3s

## 🚨 Troubleshooting

### Частые проблемы

#### Backend не запускается
```bash
# Проверка логов
docker-compose logs backend

# Проверка переменных окружения
docker-compose exec backend env | grep DATABASE

# Проверка подключения к БД
docker-compose exec backend python -c "from database.connection_pool import db_pool; print('DB OK')"
```

#### Redis connection error
```bash
# Проверка Redis
docker-compose exec redis redis-cli ping

# Проверка пароля
docker-compose exec redis redis-cli -a paygo_redis_password ping

# Проверка логов
docker-compose logs redis
```

#### Database connection error
```bash
# Проверка PostgreSQL
docker-compose exec database pg_isready -U paygo_user

# Проверка миграций
docker-compose exec backend python -m alembic current

# Проверка таблиц
docker-compose exec database psql -U paygo_user -d paygo_db -c "\dt"
```

### Performance проблемы

#### Медленные запросы
```bash
# Проверка slow query log
docker-compose exec database tail -f /var/log/postgresql/postgresql-15-main.log

# Проверка индексов
docker-compose exec database psql -U paygo_user -d paygo_db -c "\di+"

# Анализ таблиц
docker-compose exec database psql -U paygo_user -d paygo_db -c "ANALYZE;"
```

#### Высокое использование памяти
```bash
# Проверка Redis memory
docker-compose exec redis redis-cli info memory

# Проверка PostgreSQL memory
docker-compose exec database psql -U paygo_user -d paygo_db -c "SELECT * FROM pg_stat_bgwriter;"

# Проверка Docker stats
docker stats --no-stream
```

## 📚 Дополнительные ресурсы

### Документация
- [API Documentation](http://localhost:8000/docs)
- [Prometheus](http://localhost:9090)
- [Grafana](http://localhost:3001)

### Полезные команды
```bash
# Очистка Docker
docker system prune -a

# Пересборка без кеша
docker-compose build --no-cache

# Проверка размера образов
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Мониторинг в реальном времени
docker stats
```

### Контакты
- **QA Team**: qa@paygo.com
- **DevOps**: devops@paygo.com
- **Security**: security@paygo.com

---

*Последнее обновление: $(Get-Date)*
