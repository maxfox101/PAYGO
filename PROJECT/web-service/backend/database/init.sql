-- Инициализация базы данных PayGo с оптимизированными индексами

-- Создание таблиц
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(32),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_number_hash VARCHAR(255) NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    expiry_month INTEGER NOT NULL,
    expiry_year INTEGER NOT NULL,
    cardholder_name VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS terminals (
    id SERIAL PRIMARY KEY,
    terminal_id VARCHAR(50) UNIQUE NOT NULL,
    location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    terminal_type VARCHAR(50),
    firmware_version VARCHAR(20),
    hardware_version VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(id) ON DELETE SET NULL,
    terminal_id INTEGER REFERENCES terminals(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_type VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    reference_id VARCHAR(100) UNIQUE,
    merchant_id VARCHAR(100),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    ip_address INET,
    user_agent TEXT,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    ip_address INET,
    user_agent TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    priority VARCHAR(20) DEFAULT 'normal',
    metadata JSONB
);

-- ОПТИМИЗИРОВАННЫЕ ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ

-- Индексы для таблицы users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX IF NOT EXISTS idx_users_two_factor_enabled ON users(two_factor_enabled);
CREATE INDEX IF NOT EXISTS idx_users_failed_login_attempts ON users(failed_login_attempts);
CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users(locked_until);

-- Составной индекс для поиска по имени и фамилии
CREATE INDEX IF NOT EXISTS idx_users_name_search ON users USING gin(to_tsvector('english', first_name || ' ' || last_name));

-- Индексы для таблицы cards
CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id);
CREATE INDEX IF NOT EXISTS idx_cards_card_type ON cards(card_type);
CREATE INDEX IF NOT EXISTS idx_cards_is_default ON cards(is_default);
CREATE INDEX IF NOT EXISTS idx_cards_is_active ON cards(is_active);
CREATE INDEX IF NOT EXISTS idx_cards_expiry ON cards(expiry_year, expiry_month);
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at);
CREATE INDEX IF NOT EXISTS idx_cards_last_used ON cards(last_used);

-- Составной индекс для активных карт пользователя
CREATE INDEX IF NOT EXISTS idx_cards_user_active ON cards(user_id, is_active) WHERE is_active = TRUE;

-- Индексы для таблицы terminals
CREATE INDEX IF NOT EXISTS idx_terminals_terminal_id ON terminals(terminal_id);
CREATE INDEX IF NOT EXISTS idx_terminals_status ON terminals(status);
CREATE INDEX IF NOT EXISTS idx_terminals_location ON terminals(location);
CREATE INDEX IF NOT EXISTS idx_terminals_last_heartbeat ON terminals(last_heartbeat);
CREATE INDEX IF NOT EXISTS idx_terminals_created_at ON terminals(created_at);
CREATE INDEX IF NOT EXISTS idx_terminals_location_coords ON terminals USING gist (ll_to_earth(location_lat, location_lng));

-- Индексы для таблицы transactions
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_transactions_terminal_id ON transactions(terminal_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_processed_at ON transactions(processed_at);
CREATE INDEX IF NOT EXISTS idx_transactions_reference_id ON transactions(reference_id);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_currency ON transactions(currency);

-- Составные индексы для сложных запросов
CREATE INDEX IF NOT EXISTS idx_transactions_user_status ON transactions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_terminal_date ON transactions(terminal_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_amount_range ON transactions(amount) WHERE amount > 0;
CREATE INDEX IF NOT EXISTS idx_transactions_location_coords ON transactions USING gist (ll_to_earth(location_lat, location_lng));

-- Индекс для поиска по диапазону дат
CREATE INDEX IF NOT EXISTS idx_transactions_date_range ON transactions(created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';

-- Индексы для таблицы audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);

-- Составной индекс для аудита по пользователю и действию
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action, created_at DESC);

-- Индексы для таблицы sessions
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);

-- Составной индекс для активных сессий пользователя
CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, is_active) WHERE is_active = TRUE;

-- Индексы для таблицы notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);

-- Составной индекс для непрочитанных уведомлений
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- ЧАСТИЧНЫЕ ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ

-- Индекс только для активных пользователей
CREATE INDEX IF NOT EXISTS idx_users_active_only ON users(id, username, email) WHERE is_active = TRUE;

-- Индекс только для активных карт
CREATE INDEX IF NOT EXISTS idx_cards_active_only ON cards(id, user_id, card_type) WHERE is_active = TRUE;

-- Индекс только для успешных транзакций
CREATE INDEX IF NOT EXISTS idx_transactions_successful ON transactions(id, user_id, amount, created_at) WHERE status = 'completed';

-- Индекс только для активных сессий
CREATE INDEX IF NOT EXISTS idx_sessions_active_only ON sessions(id, user_id, last_activity) WHERE is_active = TRUE AND expires_at > CURRENT_TIMESTAMP;

-- ИНДЕКСЫ ДЛЯ ПОЛНОТЕКСТОВОГО ПОИСКА

-- Индекс для поиска по описанию транзакций
CREATE INDEX IF NOT EXISTS idx_transactions_description_search ON transactions USING gin(to_tsvector('english', description));

-- Индекс для поиска по метаданным (JSONB)
CREATE INDEX IF NOT EXISTS idx_transactions_metadata ON transactions USING gin(metadata);

-- Индекс для поиска по деталям аудита
CREATE INDEX IF NOT EXISTS idx_audit_logs_details ON audit_logs USING gin(details);

-- ИНДЕКСЫ ДЛЯ ГЕОГРАФИЧЕСКИХ ДАННЫХ

-- Индекс для поиска терминалов по расстоянию
CREATE INDEX IF NOT EXISTS idx_terminals_geo ON terminals USING gist (ll_to_earth(location_lat, location_lng));

-- Индекс для поиска транзакций по местоположению
CREATE INDEX IF NOT EXISTS idx_transactions_geo ON transactions USING gist (ll_to_earth(location_lat, location_lng));

-- ИНДЕКСЫ ДЛЯ ВРЕМЕННЫХ РЯДОВ

-- Индекс для агрегации по времени (часы, дни, месяцы)
CREATE INDEX IF NOT EXISTS idx_transactions_time_series ON transactions(date_trunc('hour', created_at), status, amount);

-- Индекс для поиска по временным окнам
CREATE INDEX IF NOT EXISTS idx_transactions_time_windows ON transactions(created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '90 days';

-- УНИКАЛЬНЫЕ ИНДЕКСЫ И ОГРАНИЧЕНИЯ

-- Уникальный индекс для reference_id транзакций
CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_reference_unique ON transactions(reference_id) WHERE reference_id IS NOT NULL;

-- Уникальный индекс для одной активной сессии на пользователя
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_user_unique ON sessions(user_id) WHERE is_active = TRUE;

-- Уникальный индекс для одной карты по умолчанию на пользователя
CREATE UNIQUE INDEX IF NOT EXISTS idx_cards_default_unique ON cards(user_id) WHERE is_default = TRUE;

-- ИНДЕКСЫ ДЛЯ СТАТИСТИКИ И АНАЛИТИКИ

-- Индекс для подсчета транзакций по пользователю
CREATE INDEX IF NOT EXISTS idx_transactions_user_count ON transactions(user_id, created_at);

-- Индекс для подсчета транзакций по терминалу
CREATE INDEX IF NOT EXISTS idx_transactions_terminal_count ON transactions(terminal_id, created_at);

-- Индекс для анализа сумм транзакций
CREATE INDEX IF NOT EXISTS idx_transactions_amount_analysis ON transactions(amount, created_at, status);

-- СОЗДАНИЕ ФУНКЦИЙ ДЛЯ ОБНОВЛЕНИЯ ВРЕМЕННЫХ МЕТОК

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cards_updated_at BEFORE UPDATE ON cards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_terminals_updated_at BEFORE UPDATE ON terminals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ФУНКЦИИ ДЛЯ ОЧИСТКИ УСТАРЕВШИХ ДАННЫХ

-- Функция для очистки старых сессий
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Функция для очистки старых уведомлений
CREATE OR REPLACE FUNCTION cleanup_old_notifications()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM notifications WHERE created_at < CURRENT_DATE - INTERVAL '90 days' AND is_read = TRUE;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ФУНКЦИИ ДЛЯ СТАТИСТИКИ

-- Функция для получения статистики пользователя
CREATE OR REPLACE FUNCTION get_user_stats(user_id_param INTEGER)
RETURNS TABLE(
    total_transactions BIGINT,
    total_amount DECIMAL,
    avg_amount DECIMAL,
    last_transaction TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_transactions,
        COALESCE(SUM(amount), 0) as total_amount,
        COALESCE(AVG(amount), 0) as avg_amount,
        MAX(created_at) as last_transaction
    FROM transactions 
    WHERE user_id = user_id_param AND status = 'completed';
END;
$$ LANGUAGE plpgsql;

-- Функция для получения статистики терминала
CREATE OR REPLACE FUNCTION get_terminal_stats(terminal_id_param INTEGER)
RETURNS TABLE(
    total_transactions BIGINT,
    total_amount DECIMAL,
    avg_amount DECIMAL,
    last_transaction TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_transactions,
        COALESCE(SUM(amount), 0) as total_amount,
        COALESCE(AVG(amount), 0) as avg_amount,
        MAX(created_at) as last_transaction
    FROM transactions 
    WHERE terminal_id = terminal_id_param AND status = 'completed';
END;
$$ LANGUAGE plpgsql;

-- СОЗДАНИЕ ПРЕДСТАВЛЕНИЙ ДЛЯ ЧАСТО ИСПОЛЬЗУЕМЫХ ЗАПРОСОВ

-- Представление для активных пользователей с их картами
CREATE OR REPLACE VIEW active_users_with_cards AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    u.phone,
    u.created_at,
    u.last_login,
    COUNT(c.id) as active_cards_count,
    MAX(c.last_used) as last_card_usage
FROM users u
LEFT JOIN cards c ON u.id = c.user_id AND c.is_active = TRUE
WHERE u.is_active = TRUE
GROUP BY u.id, u.username, u.email, u.first_name, u.last_name, u.phone, u.created_at, u.last_login;

-- Представление для статистики транзакций по дням
CREATE OR REPLACE VIEW daily_transaction_stats AS
SELECT 
    DATE(created_at) as transaction_date,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_transactions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_transactions,
    COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_amount,
    COALESCE(AVG(CASE WHEN status = 'completed' THEN amount END), 0) as avg_amount
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY transaction_date DESC;

-- Представление для активных терминалов с последней активностью
CREATE OR REPLACE VIEW active_terminals_status AS
SELECT 
    t.id,
    t.terminal_id,
    t.location,
    t.status,
    t.last_heartbeat,
    t.terminal_type,
    t.firmware_version,
    COUNT(tr.id) as transactions_today,
    COALESCE(SUM(CASE WHEN tr.status = 'completed' THEN tr.amount ELSE 0 END), 0) as amount_today
FROM terminals t
LEFT JOIN transactions tr ON t.id = tr.terminal_id 
    AND DATE(tr.created_at) = CURRENT_DATE
WHERE t.status = 'active'
GROUP BY t.id, t.terminal_id, t.location, t.status, t.last_heartbeat, t.terminal_type, t.firmware_version;

-- СОЗДАНИЕ МАТЕРИАЛИЗОВАННЫХ ПРЕДСТАВЛЕНИЙ ДЛЯ СЛОЖНЫХ АГРЕГАЦИЙ

-- Материализованное представление для ежемесячной статистики
CREATE MATERIALIZED VIEW monthly_transaction_stats AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_transactions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_transactions,
    COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_amount,
    COALESCE(AVG(CASE WHEN status = 'completed' THEN amount END), 0) as avg_amount,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT terminal_id) as unique_terminals
FROM transactions
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- Создание индекса для материализованного представления
CREATE UNIQUE INDEX idx_monthly_stats_month ON monthly_transaction_stats(month);

-- ФУНКЦИЯ ДЛЯ ОБНОВЛЕНИЯ МАТЕРИАЛИЗОВАННЫХ ПРЕДСТАВЛЕНИЙ
CREATE OR REPLACE FUNCTION refresh_monthly_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_transaction_stats;
END;
$$ LANGUAGE plpgsql;

-- СОЗДАНИЕ ПЛАНА ОБНОВЛЕНИЯ СТАТИСТИКИ
-- Рекомендуется настроить cron job для выполнения этой функции каждый час
-- SELECT refresh_monthly_stats();

-- ФИНАЛЬНАЯ ОПТИМИЗАЦИЯ

-- Анализ таблиц для оптимизации планировщика запросов
ANALYZE users;
ANALYZE cards;
ANALYZE terminals;
ANALYZE transactions;
ANALYZE audit_logs;
ANALYZE sessions;
ANALYZE notifications;

-- Создание статистики для индексов
ANALYZE;

-- Комментарии по использованию индексов
COMMENT ON INDEX idx_transactions_user_date IS 'Оптимизирует поиск транзакций пользователя по дате';
COMMENT ON INDEX idx_transactions_amount_range IS 'Оптимизирует поиск транзакций по сумме';
COMMENT ON INDEX idx_users_name_search IS 'Оптимизирует полнотекстовый поиск по имени пользователя';
COMMENT ON INDEX idx_transactions_geo IS 'Оптимизирует геопоиск транзакций';
COMMENT ON INDEX idx_terminals_geo IS 'Оптимизирует геопоиск терминалов';
