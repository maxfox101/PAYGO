from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class I18nManager:
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.locales_dir.mkdir(exist_ok=True)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_locale = "ru"
        self.supported_locales = ["ru", "en"]
        
        self._load_translations()
    
    def _load_translations(self):
        """Загрузка переводов из файлов"""
        try:
            for locale in self.supported_locales:
                locale_file = self.locales_dir / f"{locale}.json"
                if locale_file.exists():
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                    logger.info(f"✅ Загружен перевод для языка: {locale}")
                else:
                    # Создаем файл с базовыми переводами
                    self._create_default_translations(locale)
                    
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки переводов: {e}")
    
    def _create_default_translations(self, locale: str):
        """Создание файла с базовыми переводами"""
        if locale == "ru":
            default_translations = {
                "common": {
                    "save": "Сохранить",
                    "cancel": "Отмена",
                    "delete": "Удалить",
                    "edit": "Редактировать",
                    "add": "Добавить",
                    "search": "Поиск",
                    "loading": "Загрузка...",
                    "error": "Ошибка",
                    "success": "Успешно",
                    "warning": "Предупреждение"
                },
                "auth": {
                    "login": "Вход",
                    "logout": "Выход",
                    "register": "Регистрация",
                    "email": "Email",
                    "password": "Пароль",
                    "confirm_password": "Подтвердите пароль",
                    "forgot_password": "Забыли пароль?",
                    "login_success": "Вход выполнен успешно",
                    "login_failed": "Ошибка входа"
                },
                "transactions": {
                    "amount": "Сумма",
                    "currency": "Валюта",
                    "status": "Статус",
                    "date": "Дата",
                    "description": "Описание",
                    "successful": "Успешно",
                    "failed": "Неудачно",
                    "pending": "В обработке"
                },
                "notifications": {
                    "push_enabled": "Push-уведомления включены",
                    "push_disabled": "Push-уведомления отключены",
                    "email_enabled": "Email-уведомления включены",
                    "email_disabled": "Email-уведомления отключены"
                }
            }
        else:  # en
            default_translations = {
                "common": {
                    "save": "Save",
                    "cancel": "Cancel",
                    "delete": "Delete",
                    "edit": "Edit",
                    "add": "Add",
                    "search": "Search",
                    "loading": "Loading...",
                    "error": "Error",
                    "success": "Success",
                    "warning": "Warning"
                },
                "auth": {
                    "login": "Login",
                    "logout": "Logout",
                    "register": "Register",
                    "email": "Email",
                    "password": "Password",
                    "confirm_password": "Confirm Password",
                    "forgot_password": "Forgot Password?",
                    "login_success": "Login successful",
                    "login_failed": "Login failed"
                },
                "transactions": {
                    "amount": "Amount",
                    "currency": "Currency",
                    "status": "Status",
                    "date": "Date",
                    "description": "Description",
                    "successful": "Successful",
                    "failed": "Failed",
                    "pending": "Pending"
                },
                "notifications": {
                    "push_enabled": "Push notifications enabled",
                    "push_disabled": "Push notifications disabled",
                    "email_enabled": "Email notifications enabled",
                    "email_disabled": "Email notifications disabled"
                }
            }
        
        locale_file = self.locales_dir / f"{locale}.json"
        with open(locale_file, 'w', encoding='utf-8') as f:
            json.dump(default_translations, f, ensure_ascii=False, indent=2)
        
        self.translations[locale] = default_translations
        logger.info(f"✅ Создан файл переводов для языка: {locale}")
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """Получение перевода по ключу"""
        if locale is None:
            locale = self.default_locale
        
        if locale not in self.supported_locales:
            locale = self.default_locale
        
        # Разбиваем ключ на части (например: "common.save")
        keys = key.split('.')
        translation = self.translations.get(locale, {})
        
        # Проходим по вложенным ключам
        for k in keys:
            if isinstance(translation, dict) and k in translation:
                translation = translation[k]
            else:
                # Если перевод не найден, возвращаем ключ
                logger.warning(f"⚠️ Перевод не найден: {key} для языка {locale}")
                return key
        
        # Если перевод найден и это строка
        if isinstance(translation, str):
            # Заменяем плейсхолдеры
            try:
                return translation.format(**kwargs)
            except KeyError:
                logger.warning(f"⚠️ Неверные плейсхолдеры в переводе: {key}")
                return translation
        
        return str(translation)
    
    def get_locale_texts(self, locale: str = None) -> Dict[str, Any]:
        """Получение всех переводов для языка"""
        if locale is None:
            locale = self.default_locale
        
        if locale not in self.supported_locales:
            locale = self.default_locale
        
        return self.translations.get(locale, {})
    
    def add_translation(self, locale: str, key: str, value: str):
        """Добавление нового перевода"""
        if locale not in self.supported_locales:
            logger.error(f"❌ Неподдерживаемый язык: {locale}")
            return False
        
        if locale not in self.translations:
            self.translations[locale] = {}
        
        # Разбиваем ключ на части
        keys = key.split('.')
        current = self.translations[locale]
        
        # Создаем вложенную структуру
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Устанавливаем значение
        current[keys[-1]] = value
        
        # Сохраняем в файл
        self._save_translations(locale)
        logger.info(f"✅ Добавлен перевод: {key} = {value} для языка {locale}")
        return True
    
    def _save_translations(self, locale: str):
        """Сохранение переводов в файл"""
        try:
            locale_file = self.locales_dir / f"{locale}.json"
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[locale], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения переводов для {locale}: {e}")
    
    def get_supported_locales(self) -> list:
        """Получение списка поддерживаемых языков"""
        return self.supported_locales.copy()
    
    def set_default_locale(self, locale: str):
        """Установка языка по умолчанию"""
        if locale in self.supported_locales:
            self.default_locale = locale
            logger.info(f"✅ Установлен язык по умолчанию: {locale}")
        else:
            logger.error(f"❌ Неподдерживаемый язык: {locale}")

# Глобальный экземпляр менеджера переводов
i18n = I18nManager()

