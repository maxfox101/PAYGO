from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TerminalStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class PaymentMethod(str, Enum):
    NFC = "nfc"
    QR_CODE = "qr_code"
    BIOMETRIC = "biometric"
    CARD_INSERT = "card_insert"

class TerminalType(str, Enum):
    STANDALONE = "standalone"
    INTEGRATED = "integrated"
    MOBILE = "mobile"

class TerminalBase(BaseModel):
    name: str
    location: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    terminal_type: TerminalType
    supported_payment_methods: List[PaymentMethod]
    is_active: bool = True

class TerminalCreate(TerminalBase):
    serial_number: str
    model: str
    manufacturer: str

class TerminalUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    supported_payment_methods: Optional[List[PaymentMethod]] = None
    is_active: Optional[bool] = None

class TerminalHardware(BaseModel):
    cpu_usage: float
    memory_usage: float
    storage_usage: float
    temperature: float
    uptime: int  # в секундах
    last_reboot: datetime
    firmware_version: str
    has_printer: bool = True
    has_nfc_reader: bool = True
    has_camera: bool = True
    has_fingerprint_scanner: bool = False

class TerminalConfiguration(BaseModel):
    max_transaction_amount: float = 50000.0  # рублей
    min_transaction_amount: float = 1.0
    session_timeout: int = 300  # секунд
    receipt_print_enabled: bool = True
    sound_enabled: bool = True
    language: str = "ru"
    currency: str = "RUB"
    tax_rate: float = 0.20
    merchant_id: str
    acquiring_settings: Dict[str, Any] = {}

class Terminal(TerminalBase):
    id: str
    serial_number: str
    model: str
    manufacturer: str
    status: TerminalStatus
    created_at: datetime
    updated_at: datetime
    last_ping: Optional[datetime] = None
    software_version: str
    hardware: Optional[TerminalHardware] = None
    configuration: Optional[TerminalConfiguration] = None
    
    class Config:
        from_attributes = True

class TerminalStats(BaseModel):
    terminal_id: str
    date: datetime
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    total_amount: float
    average_transaction_amount: float
    uptime_percentage: float
    error_count: int

class TerminalLog(BaseModel):
    id: Optional[str] = None
    terminal_id: str
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    component: Optional[str] = None  # payment, hardware, network, etc.
    additional_data: Optional[Dict[str, Any]] = None

class TerminalCommand(BaseModel):
    id: Optional[str] = None
    terminal_id: str
    command_type: str  # reboot, update, configure, etc.
    command_data: Dict[str, Any]
    created_at: datetime
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[str] = None

class TerminalHealthCheck(BaseModel):
    terminal_id: str
    timestamp: datetime
    status: TerminalStatus
    hardware: TerminalHardware
    network_latency: float
    last_transaction: Optional[datetime] = None
    errors: List[str] = []
    warnings: List[str] = [] 