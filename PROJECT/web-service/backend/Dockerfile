# Многоэтапная сборка для оптимизации размера и безопасности
FROM python:3.11-slim as builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim as runtime

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libpq5 \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    liblcms2-2 \
    libwebp6 \
    libopenjp2-7 \
    libtiff5 \
    libharfbuzz0b \
    libfribidi0 \
    libxcb1 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создание пользователя для безопасности
RUN groupadd -r paygo && useradd -r -g paygo paygo

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание рабочих директорий
WORKDIR /app

# Копирование исходного кода
COPY --chown=paygo:paygo . .

# Создание директорий для логов и временных файлов
RUN mkdir -p /app/logs /app/tmp /app/uploads && \
    chown -R paygo:paygo /app/logs /app/tmp /app/uploads

# Установка прав доступа
RUN chmod +x /app/run.py && \
    chmod +x /app/simple_main.py

# Переключение на непривилегированного пользователя
USER paygo

# Проверка здоровья приложения
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONHASHSEED=random

# Оптимизация Python
ENV PYTHONOPTIMIZE=2
ENV PYTHONFAULTHANDLER=1

# Настройки для производительности
ENV PYTHONMALLOC=malloc
ENV PYTHONDEVMODE=0

# Порт приложения
EXPOSE 8000

# Команда запуска с оптимизациями
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop", "--http", "httptools"] 