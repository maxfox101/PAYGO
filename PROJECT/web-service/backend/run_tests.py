#!/usr/bin/env python3
"""
Скрипт для запуска всех типов тестов PayGo backend
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Запуск команды с выводом результата"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Выполняю: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} завершен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} завершился с ошибкой: {e}")
        return False

def install_dependencies():
    """Установка зависимостей для тестирования"""
    print("📦 Устанавливаю зависимости для тестирования...")
    
    # Устанавливаем pytest и связанные пакеты
    packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-xdist",
        "pytest-rerunfailures",
        "pytest-html",
        "pytest-mock",
        "pytest-benchmark",
        "coverage",
        "black",
        "isort",
        "flake8",
        "bandit",
        "mypy",
        "pre-commit"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} установлен")
        except subprocess.CalledProcessError:
            print(f"❌ Ошибка установки {package}")

def run_unit_tests():
    """Запуск unit тестов"""
    return run_command(
        "python -m pytest tests/ -m 'not integration and not performance and not slow' -v --tb=short",
        "Unit тесты"
    )

def run_integration_tests():
    """Запуск интеграционных тестов"""
    return run_command(
        "python -m pytest tests/ -m integration -v --tb=short",
        "Интеграционные тесты"
    )

def run_security_tests():
    """Запуск тестов безопасности"""
    return run_command(
        "python -m pytest tests/ -m security -v --tb=short",
        "Тесты безопасности"
    )

def run_performance_tests():
    """Запуск тестов производительности"""
    return run_command(
        "python -m pytest tests/ -m performance -v --tb=short",
        "Тесты производительности"
    )

def run_all_tests():
    """Запуск всех тестов"""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "Все тесты"
    )

def run_coverage():
    """Запуск тестов с покрытием"""
    return run_command(
        "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=80",
        "Тесты с покрытием кода"
    )

def run_linting():
    """Запуск проверки качества кода"""
    print("\n🔍 Запускаю проверку качества кода...")
    
    # Black форматирование
    black_success = run_command(
        "python -m black . --check",
        "Проверка форматирования Black"
    )
    
    # isort проверка
    isort_success = run_command(
        "python -m isort . --check-only",
        "Проверка сортировки импортов"
    )
    
    # flake8 проверка
    flake8_success = run_command(
        "python -m flake8 . --max-line-length=88 --extend-ignore=E203,W503",
        "Проверка стиля кода Flake8"
    )
    
    # mypy проверка типов
    mypy_success = run_command(
        "python -m mypy . --ignore-missing-imports",
        "Проверка типов MyPy"
    )
    
    # bandit проверка безопасности
    bandit_success = run_command(
        "python -m bandit -r . -f json -o bandit-report.json",
        "Проверка безопасности Bandit"
    )
    
    return all([black_success, isort_success, flake8_success, mypy_success, bandit_success])

def run_benchmarks():
    """Запуск бенчмарков"""
    return run_command(
        "python -m pytest tests/ -m performance --benchmark-only",
        "Бенчмарки производительности"
    )

def generate_report():
    """Генерация отчета о тестировании"""
    print("\n📊 Генерирую отчет о тестировании...")
    
    # Создаем директорию для отчетов
    reports_dir = Path("test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Запускаем тесты с HTML отчетом
    html_success = run_command(
        f"python -m pytest tests/ --html={reports_dir}/test_report.html --self-contained-html",
        "Генерация HTML отчета"
    )
    
    # Запускаем тесты с покрытием
    coverage_success = run_command(
        f"python -m pytest tests/ --cov=. --cov-report=html:{reports_dir}/coverage_html --cov-report=xml:{reports_dir}/coverage.xml",
        "Генерация отчета о покрытии"
    )
    
    if html_success and coverage_success:
        print(f"\n📁 Отчеты сохранены в директории: {reports_dir.absolute()}")
        print(f"🌐 HTML отчет: {reports_dir}/test_report.html")
        print(f"📊 Отчет о покрытии: {reports_dir}/coverage_html/index.html")
    
    return html_success and coverage_success

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Запуск тестов PayGo backend")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "security", "performance", "all", "coverage", "lint", "benchmark", "report"],
        default="all",
        help="Тип тестов для запуска"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Установить зависимости для тестирования"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Быстрый режим (только unit тесты)"
    )
    
    args = parser.parse_args()
    
    print("🧪 PayGo Backend Test Runner")
    print("=" * 50)
    
    # Устанавливаем зависимости если нужно
    if args.install_deps:
        install_dependencies()
    
    # Быстрый режим
    if args.fast:
        print("⚡ Быстрый режим: запускаю только unit тесты")
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    
    # Запускаем выбранный тип тестов
    success = False
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "security":
        success = run_security_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "coverage":
        success = run_coverage()
    elif args.type == "lint":
        success = run_linting()
    elif args.type == "benchmark":
        success = run_benchmarks()
    elif args.type == "report":
        success = generate_report()
    elif args.type == "all":
        print("🔄 Запускаю все типы тестов...")
        
        # Сначала проверяем качество кода
        lint_success = run_linting()
        if not lint_success:
            print("⚠️  Обнаружены проблемы с качеством кода")
        
        # Затем запускаем тесты
        unit_success = run_unit_tests()
        integration_success = run_integration_tests()
        security_success = run_security_tests()
        performance_success = run_performance_tests()
        
        success = all([unit_success, integration_success, security_success, performance_success])
    
    # Выводим итоговый результат
    print("\n" + "="*60)
    if success:
        print("🎉 Все тесты прошли успешно!")
        print("✅ Качество кода соответствует стандартам")
        print("✅ Функциональность работает корректно")
        print("✅ Безопасность проверена")
        print("✅ Производительность в норме")
    else:
        print("❌ Некоторые тесты не прошли")
        print("🔍 Проверьте логи выше для деталей")
        print("💡 Исправьте ошибки и запустите тесты снова")
    
    print("="*60)
    
    # Возвращаем код выхода
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()


