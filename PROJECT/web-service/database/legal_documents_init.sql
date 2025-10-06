-- Создание таблиц для правовых документов

-- Таблица правовых документов
CREATE TABLE IF NOT EXISTS legal_documents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL CHECK (type IN ('offer', 'terms', 'privacy', 'agreement')),
    version VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    requires_acceptance BOOLEAN DEFAULT TRUE,
    effective_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица принятия документов пользователями
CREATE TABLE IF NOT EXISTS user_document_acceptances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES legal_documents(id) ON DELETE CASCADE,
    UNIQUE(user_id, document_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_legal_documents_type ON legal_documents(type);
CREATE INDEX IF NOT EXISTS idx_legal_documents_active ON legal_documents(is_active);
CREATE INDEX IF NOT EXISTS idx_legal_documents_effective_date ON legal_documents(effective_date);
CREATE INDEX IF NOT EXISTS idx_user_document_acceptances_user_id ON user_document_acceptances(user_id);
CREATE INDEX IF NOT EXISTS idx_user_document_acceptances_document_id ON user_document_acceptances(document_id);

-- Вставка начальных правовых документов

-- Публичная оферта
INSERT INTO legal_documents (type, version, title, content, requires_acceptance, effective_date) VALUES (
    'offer',
    '1.0.0',
    'ПУБЛИЧНАЯ ОФЕРТА на оказание услуг пользования системой PayGo',
    '<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Публичная оферта PayGo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #222; }
        h1, h2, h3, h4 { color: #ff6b35; margin-bottom: 10px; }
        p, ul, li { margin-bottom: 10px; }
        ul { padding-left: 20px; }
        strong { font-weight: bold; }
    </style>
</head>
<body>
    <h1>ПУБЛИЧНАЯ ОФЕРТА</h1>
    <h2>Об оказании услуг пользования системой PayGo</h2>
    
    <p><strong>ООО «PayGo»</strong>, именуемое в дальнейшем «Оператор», размещает настоящую оферту (предложение) любым физическим и/или юридическим лицам (далее — «Пользователь») заключить договор на условиях, изложенных ниже.</p>
    
    <h3>1. Предмет оферты</h3>
    <p>1.1. Оператор предоставляет Пользователю доступ к платформе PayGo — системе электронных платежей, управлению банковскими картами, использованию терминалов, сервису денежных переводов и сопутствующим сервисам.</p>
    <p>1.2. Услуги предоставляются через веб-интерфейс, мобильные и десктопные приложения, терминалы самообслуживания.</p>
    
    <h3>2. Принятие условий оферты</h3>
    <p>2.1. Договор считается заключённым с момента регистрации в системе PayGo, начала использования Личного кабинета, установки приложения, либо с момента совершения любого действия по использованию системы.</p>
    <p>2.2. Принятие условий настоящей Оферты (акцепт) является эквивалентом подписания письменного договора.</p>
    
    <h3>3. Регистрация и авторизация</h3>
    <p>3.1. Для получения доступа к сервисам требуется регистрация с предоставлением достоверных персональных данных и контактной информации.</p>
    <p>3.2. Пользователь обязуется использовать только собственные, корректные и актуальные данные.</p>
    <p>3.3. Оператор вправе в любой момент запросить подтверждение личности и/или дополнительную авторизацию (SMS, биометрические данные, двухфакторная аутентификация).</p>
    
    <h3>4. Персональные данные</h3>
    <p>4.1. Оператор обрабатывает персональные данные Пользователя в соответствии с Политикой конфиденциальности.</p>
    <p>4.2. Пользователь даёт согласие на обработку персональных данных при регистрации в системе.</p>
    
    <h3>5. Оплата услуг</h3>
    <p>5.1. Тарифы на услуги публикуются на сайте Оператора и могут изменяться в одностороннем порядке.</p>
    <p>5.2. Оплата производится в соответствии с выбранным тарифным планом.</p>
    
    <h3>6. Ответственность сторон</h3>
    <p>6.1. Оператор несёт ответственность за качество предоставляемых услуг в соответствии с законодательством РФ.</p>
    <p>6.2. Пользователь несёт ответственность за соблюдение условий использования системы.</p>
    
    <h3>7. Заключительные положения</h3>
    <p>7.1. Настоящая оферта вступает в силу с момента размещения на сайте Оператора.</p>
    <p>7.2. Оператор оставляет за собой право изменять условия оферты с уведомлением Пользователей.</p>
    
    <p><strong>Дата размещения:</strong> 2024-01-01</p>
    <p><strong>Версия:</strong> 1.0.0</p>
</body>
</html>',
    TRUE,
    CURRENT_TIMESTAMP
);

-- Условия использования
INSERT INTO legal_documents (type, version, title, content, requires_acceptance, effective_date) VALUES (
    'terms',
    '1.0.0',
    'УСЛОВИЯ ИСПОЛЬЗОВАНИЯ системы PayGo',
    '<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Условия использования PayGo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #222; }
        h1, h2, h3, h4 { color: #ff6b35; margin-bottom: 10px; }
        p, ul, li { margin-bottom: 10px; }
        ul { padding-left: 20px; }
        strong { font-weight: bold; }
    </style>
</head>
<body>
    <h1>УСЛОВИЯ ИСПОЛЬЗОВАНИЯ</h1>
    <h2>Системы PayGo</h2>
    
    <h3>1. Общие положения</h3>
    <p>1.1. Настоящие Условия использования регулируют порядок использования системы PayGo.</p>
    <p>1.2. Использование системы означает согласие с настоящими Условиями.</p>
    
    <h3>2. Правила использования</h3>
    <p>2.1. Запрещается использование системы для незаконной деятельности.</p>
    <p>2.2. Пользователь обязуется не нарушать работу системы.</p>
    
    <h3>3. Безопасность</h3>
    <p>3.1. Пользователь несёт ответственность за безопасность своих учётных данных.</p>
    <p>3.2. При подозрении на компрометацию данных необходимо немедленно сменить пароль.</p>
    
    <p><strong>Дата вступления в силу:</strong> 2024-01-01</p>
    <p><strong>Версия:</strong> 1.0.0</p>
</body>
</html>',
    TRUE,
    CURRENT_TIMESTAMP
);

-- Политика конфиденциальности
INSERT INTO legal_documents (type, version, title, content, requires_acceptance, effective_date) VALUES (
    'privacy',
    '1.0.0',
    'ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ системы PayGo',
    '<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Политика конфиденциальности PayGo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #222; }
        h1, h2, h3, h4 { color: #ff6b35; margin-bottom: 10px; }
        p, ul, li { margin-bottom: 10px; }
        ul { padding-left: 20px; }
        strong { font-weight: bold; }
    </style>
</head>
<body>
    <h1>ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ</h1>
    <h2>Системы PayGo</h2>
    
    <h3>1. Сбор информации</h3>
    <p>1.1. Мы собираем только необходимую для работы системы информацию.</p>
    <p>1.2. Персональные данные обрабатываются в соответствии с законодательством РФ.</p>
    
    <h3>2. Использование информации</h3>
    <p>2.1. Собранная информация используется исключительно для предоставления услуг.</p>
    <p>2.2. Информация не передаётся третьим лицам без согласия пользователя.</p>
    
    <h3>3. Защита данных</h3>
    <p>3.1. Применяются современные методы защиты персональных данных.</p>
    <p>3.2. Доступ к данным ограничен и контролируется.</p>
    
    <p><strong>Дата вступления в силу:</strong> 2024-01-01</p>
    <p><strong>Версия:</strong> 1.0.0</p>
</body>
</html>',
    TRUE,
    CURRENT_TIMESTAMP
);

-- Пользовательское соглашение
INSERT INTO legal_documents (type, version, title, content, requires_acceptance, effective_date) VALUES (
    'agreement',
    '1.0.0',
    'ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ системы PayGo',
    '<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Пользовательское соглашение PayGo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #222; }
        h1, h2, h3, h4 { color: #ff6b35; margin-bottom: 10px; }
        p, ul, li { margin-bottom: 10px; }
        ul { padding-left: 20px; }
        strong { font-weight: bold; }
    </style>
</head>
<body>
    <h1>ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ</h1>
    <h2>Системы PayGo</h2>
    
    <h3>1. Предмет соглашения</h3>
    <p>1.1. Настоящее соглашение регулирует отношения между пользователем и системой PayGo.</p>
    <p>1.2. Соглашение вступает в силу с момента регистрации пользователя.</p>
    
    <h3>2. Права и обязанности</h3>
    <p>2.1. Пользователь имеет право на получение услуг в соответствии с тарифами.</p>
    <p>2.2. Пользователь обязуется соблюдать правила использования системы.</p>
    
    <h3>3. Срок действия</h3>
    <p>3.1. Соглашение действует бессрочно до его расторжения.</p>
    <p>3.2. Расторжение возможно по инициативе любой из сторон.</p>
    
    <p><strong>Дата вступления в силу:</strong> 2024-01-01</p>
    <p><strong>Версия:</strong> 1.0.0</p>
</body>
</html>',
    TRUE,
    CURRENT_TIMESTAMP
);

-- Создание представления для удобного просмотра активных документов
CREATE OR REPLACE VIEW active_legal_documents AS
SELECT 
    id,
    type,
    version,
    title,
    requires_acceptance,
    effective_date,
    created_at
FROM legal_documents 
WHERE is_active = TRUE
ORDER BY type, effective_date DESC;

-- Создание представления для статистики принятия документов
CREATE OR REPLACE VIEW document_acceptance_stats AS
SELECT 
    ld.id,
    ld.type,
    ld.version,
    ld.title,
    COUNT(uda.id) as total_acceptances,
    MAX(uda.accepted_at) as last_acceptance
FROM legal_documents ld
LEFT JOIN user_document_acceptances uda ON ld.id = uda.document_id
WHERE ld.is_active = TRUE
GROUP BY ld.id, ld.type, ld.version, ld.title
ORDER BY ld.type, ld.effective_date DESC;
