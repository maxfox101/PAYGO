#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска PayGo API без Docker
Запустите этот файл двойным кликом или через командную строку
"""

import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("🚀 PayGo - ЗАПУСК ПРОСТОЙ ВЕРСИИ")
    print("=" * 60)
    print()
    
    # Проверяем, что мы в правильной директории
    current_dir = os.getcwd()
    if not current_dir.endswith('PayGo'):
        print("❌ Ошибка: запустите скрипт из папки PayGo!")
        print(f"Текущая директория: {current_dir}")
        input("Нажмите Enter для выхода...")
        return
    
    # Переходим в папку backend
    backend_dir = os.path.join(current_dir, "PROJECT", "web-service", "backend")
    if not os.path.exists(backend_dir):
        print("❌ Ошибка: папка backend не найдена!")
        print(f"Ожидаемая директория: {backend_dir}")
        input("Нажмите Enter для выхода...")
        return
    
    print("[1] Переходим в папку backend...")
    os.chdir(backend_dir)
    print("✓ Перешли в папку backend")
    
    # Проверяем Python
    print("[2] Проверяем Python...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Python доступен: {result.stdout.strip()}")
    except Exception as e:
        print("❌ Ошибка: Python не доступен!")
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")
        return
    
    # Устанавливаем зависимости
    print("[3] Устанавливаем зависимости...")
    print("Устанавливаем необходимые пакеты...")
    
    packages = ["fastapi", "uvicorn[standard]", "pydantic"]
    for package in packages:
        try:
            print(f"Устанавливаем {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✓ {package} установлен")
        except subprocess.CalledProcessError:
            print(f"⚠️ Не удалось установить {package}, продолжаем...")
    
    # Проверяем наличие simple_main.py
    if not os.path.exists("simple_main.py"):
        print("❌ Ошибка: файл simple_main.py не найден!")
        input("Нажмите Enter для выхода...")
        return
    
    print("[4] Запускаем API сервер...")
    print()
    print("🚀 Запускаем PayGo API...")
    print("📍 Адрес: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/api/docs")
    print("💓 Здоровье: http://localhost:8000/api/health")
    print()
    print("Нажмите Ctrl+C для остановки сервера")
    print("-" * 60)
    
    # Даем время на чтение сообщения
    time.sleep(2)
    
    # Запускаем сервер
    try:
        subprocess.run([sys.executable, "simple_main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()



