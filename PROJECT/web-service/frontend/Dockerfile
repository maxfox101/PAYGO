# Многоэтапная сборка для оптимизации размера и производительности
FROM node:18-alpine as builder

# Установка системных зависимостей
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Создание рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production --silent

# Копирование исходного кода
COPY . .

# Сборка приложения для продакшена
RUN npm run build

# Финальный образ на основе nginx
FROM nginx:alpine as runtime

# Установка дополнительных утилит
RUN apk add --no-cache \
    curl \
    bash \
    && rm -rf /var/cache/apk/*

# Копирование собранного приложения
COPY --from=builder /app/build /usr/share/nginx/html

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Создание пользователя для безопасности
RUN addgroup -g 1001 -S nginx-user && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx-user -g nginx-user nginx-user

# Создание необходимых директорий
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chown -R nginx-user:nginx-user /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# Настройка прав доступа
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /usr/share/nginx/html

# Создание скрипта для проверки здоровья
RUN echo '#!/bin/bash\ncurl -f http://localhost/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Проверка здоровья приложения
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

# Переключение на непривилегированного пользователя
USER nginx-user

# Открытие порта
EXPOSE 80

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"] 