# Структура проекта PayGo

## Новая организация проекта

После реорганизации проект PayGo имеет четкую и логичную структуру:

```
C:\German\PayGo\           # Корневая папка
├── PROJECT/                # Основной проект
│   ├── web-service/        # Веб-сервис
│   │   ├── backend/        # FastAPI backend
│   │   ├── frontend/       # React frontend
│   │   ├── database/       # База данных PostgreSQL
│   │   └── api/            # API компоненты
│   ├── terminal/           # Терминальное ПО
│   ├── config/             # Конфигурации
│   ├── docs/               # Документация
│   ├── scripts/            # Скрипты проекта
│   ├── .github/            # CI/CD конфигурации
│   ├── README.md            # Документация проекта
│   └── docker-compose.yml  # Docker конфигурация
└── scripts/                 # Утилиты для управления
    ├── reorganize_project.bat      # Полная реорганизация
    ├── move_to_project.bat         # Перенос в PROJECT
    ├── cleanup_after_move.bat      # Очистка после переноса
    ├── cleanup_duplicates.bat      # Очистка дубликатов
    ├── run_tests.bat               # Запуск тестов
    ├── health_check.bat            # Проверка здоровья
    └── docker_ops.bat              # Docker операции
```

## Преимущества новой структуры

### 1. **Четкое разделение**
- **PROJECT/** - содержит весь код и конфигурации проекта
- **scripts/** - содержит утилиты для управления проектом

### 2. **Упрощение навигации**
- Все файлы проекта находятся в одном месте
- Легко найти нужные компоненты
- Нет путаницы с дубликатами

### 3. **Удобство управления**
- Скрипты для автоматизации задач
- Четкие инструкции по использованию
- Простота развертывания

## Работа с проектом

### Переход в проект
```cmd
cd C:\German\PayGo\PROJECT
```

### Запуск Docker
```cmd
cd C:\German\PayGo\PROJECT
docker-compose up -d
```

### Запуск тестов
```cmd
cd C:\German\PayGo\scripts
run_tests.bat
```

### Проверка здоровья
```cmd
cd C:\German\PayGo\scripts
health_check.bat
```

## Скрипты управления

### 1. **reorganize_project.bat** - Полная реорганизация
Выполняет весь процесс:
- Создание папки PROJECT
- Перенос всех файлов проекта
- Очистка дубликатов
- Удаление нерелевантных файлов

### 2. **move_to_project.bat** - Только перенос
Переносит файлы в PROJECT без удаления

### 3. **cleanup_after_move.bat** - Только очистка
Удаляет дубликаты после переноса

### 4. **cleanup_duplicates.bat** - Очистка дубликатов
Удаляет дублирующиеся папки и файлы

## Компоненты проекта

### Web Service
- **Backend**: FastAPI с Redis кешированием
- **Frontend**: React с lazy loading
- **Database**: PostgreSQL с connection pooling
- **API**: RESTful API для интеграции

### Terminal
- **Hardware**: Raspberry Pi / Orange Pi
- **Software**: C++ и Python
- **Features**: NFC, QR-коды, биометрия

### Configuration
- **Docker**: docker-compose.yml
- **Nginx**: nginx.conf
- **Prometheus**: prometheus.yml
- **Environment**: переменные окружения

### Documentation
- **API**: OpenAPI/Swagger
- **Development**: руководство разработчика
- **Deployment**: инструкции по развертыванию
- **Testing**: руководство по тестированию

## CI/CD Pipeline

### GitHub Actions
- **Testing**: автоматические тесты
- **Security**: проверка безопасности
- **Build**: сборка Docker образов
- **Deploy**: автоматическое развертывание

### Мониторинг
- **Prometheus**: метрики и алерты
- **Grafana**: дашборды
- **Logging**: централизованное логирование

## Следующие шаги

После реорганизации:

1. **Тестирование**: убедиться, что все работает
2. **Документация**: обновить README и инструкции
3. **CI/CD**: проверить pipeline
4. **Мониторинг**: настроить алерты
5. **Развертывание**: подготовить к продакшену

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f [service]`
2. Используйте скрипты в папке `scripts/`
3. Обратитесь к документации в `PROJECT/docs/`
4. Создайте issue в GitHub

---

**Важно**: После реорганизации всегда работайте из папки `PROJECT/`!
