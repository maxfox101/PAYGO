from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from databases import Database
import os
from typing import AsyncGenerator

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paygo_user:paygo_password@localhost:5432/paygo_db")

# SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Databases для async
database = Database(DATABASE_URL)

# Модели SQLAlchemy
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    date_of_birth = Column(DateTime, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    cards = relationship("Card", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    biometric_templates = relationship("BiometricTemplate", back_populates="user")
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    masked_number = Column(String, nullable=False)  # **** **** **** 1234
    bank_name = Column(String, nullable=False)
    card_type = Column(String, nullable=False)  # debit, credit
    is_primary = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    token = Column(String, nullable=False)  # Токен для безопасности
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card")

class Terminal(Base):
    __tablename__ = "terminals"
    
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    terminal_type = Column(String, nullable=False)
    status = Column(String, default="offline")
    model = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    software_version = Column(String, nullable=True)
    supported_payment_methods = Column(JSON, nullable=True)
    hardware_info = Column(JSON, nullable=True)
    configuration = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_ping = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="terminal")
    logs = relationship("TerminalLog", back_populates="terminal")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    terminal_id = Column(Integer, ForeignKey("terminals.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="RUB")
    status = Column(String, nullable=False)  # pending, completed, failed, cancelled
    payment_method = Column(String, nullable=False)  # nfc, qr_code, biometric
    description = Column(Text, nullable=True)
    receipt_url = Column(String, nullable=True)
    external_transaction_id = Column(String, nullable=True)
    bank_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    card = relationship("Card", back_populates="transactions")
    terminal = relationship("Terminal", back_populates="transactions")

class BiometricTemplate(Base):
    __tablename__ = "biometric_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_type = Column(String, nullable=False)  # fingerprint, face, voice
    template_data = Column(Text, nullable=False)  # Зашифрованные данные
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="biometric_templates")

class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=False)
    transaction_alerts = Column(Boolean, default=True)
    security_alerts = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_settings")

class TerminalLog(Base):
    __tablename__ = "terminal_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(Integer, ForeignKey("terminals.id"), nullable=False)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)  # payment, hardware, network
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    terminal = relationship("Terminal", back_populates="logs")

# Функции для работы с БД
async def get_database() -> AsyncGenerator[Database, None]:
    try:
        await database.connect()
        yield database
    finally:
        await database.disconnect()

def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Инициализация базы данных"""
    # Создание таблиц
    Base.metadata.create_all(bind=engine)
    
    # Подключение к базе данных
    await database.connect()
    
    # Создание тестовых данных
    await create_sample_data()

async def create_sample_data():
    """Создание тестовых данных"""
    try:
        # Проверяем, есть ли уже данные
        query = "SELECT COUNT(*) as count FROM users"
        result = await database.fetch_one(query)
        
        if result and result['count'] > 0:
            print("База данных уже содержит данные")
            return
        
        # Создание тестового пользователя
        user_query = """
        INSERT INTO users (email, phone, full_name, hashed_password, role, is_active, is_verified)
        VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
        """
        
        user_id = await database.fetch_val(
            user_query,
            "nzosim@sfedu.ru",
            "+7 (928) 528-45-27",
            "Никита Зосим Кириллович",
            "$2b$12$hashed_password_here",  # В реальности будет хешированный пароль
            "user",
            True,
            True
        )
        
        # Создание тестовых карт
        cards_data = [
            ("**** **** **** 5678", "Т-банк", "debit", True, "2027-04-30", "token_tbank_123"),
            ("**** **** **** 1234", "ВТБ", "debit", False, "2026-08-31", "token_vtb_456"),
            ("**** **** **** 9876", "Альфа-банк", "credit", False, "2025-11-30", "token_alfa_789"),
        ]
        
        for card_data in cards_data:
            card_query = """
            INSERT INTO cards (user_id, masked_number, bank_name, card_type, is_primary, expires_at, token)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            await database.execute(card_query, user_id, *card_data)
        
        # Создание тестовых терминалов
        terminals_data = [
            ("PAYGO_001", "Терминал №1", "ТЦ Горизонт", "ул. Пушкинская, 10", 47.2357, 39.7015, "standalone", "online"),
            ("PAYGO_002", "Терминал №2", "Супермаркет Магнит", "пр. Ленина, 45", 47.2280, 39.7100, "integrated", "online"),
            ("PAYGO_003", "Терминал №3", "Кафе Старбакс", "ул. Большая Садовая, 123", 47.2220, 39.7200, "standalone", "offline"),
        ]
        
        for terminal_data in terminals_data:
            terminal_query = """
            INSERT INTO terminals (serial_number, name, location, address, latitude, longitude, terminal_type, status, model, manufacturer)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """
            await database.execute(terminal_query, *terminal_data, "PayGo-Pro-2025", "PayGo Systems")
        
        # Создание настроек уведомлений
        notification_query = """
        INSERT INTO notification_settings (user_id, push_notifications, sms_notifications, email_notifications)
        VALUES ($1, $2, $3, $4)
        """
        await database.execute(notification_query, user_id, True, True, False)
        
        print("Тестовые данные успешно созданы")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")

async def close_db():
    """Закрытие соединения с базой данных"""
    await database.disconnect() 