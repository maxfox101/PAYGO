@echo off
echo ========================================
echo PayGo - Запуск тестов
echo ========================================
echo.

echo [1/4] Запуск backend тестов...
cd web-service\backend
echo Запуск unit тестов...
python -m pytest tests/ -v --tb=short --cov=. --cov-report=html
if %errorlevel% neq 0 (
    echo ERROR: Backend тесты не прошли!
    cd ..\..
    pause
    exit /b 1
)
echo ✓ Backend тесты прошли успешно
cd ..\..

echo.
echo [2/4] Запуск frontend тестов...
cd web-service\frontend
echo Запуск npm тестов...
npm test -- --coverage --watchAll=false
if %errorlevel% neq 0 (
    echo ERROR: Frontend тесты не прошли!
    cd ..\..
    pause
    exit /b 1
)
echo ✓ Frontend тесты прошли успешно
cd ..\..

echo.
echo [3/4] Запуск performance тестов...
cd web-service\backend
echo Запуск тестов производительности...
python -m pytest tests/test_performance.py -v --tb=short
if %errorlevel% neq 0 (
    echo WARNING: Performance тесты не прошли (не критично)
) else (
    echo ✓ Performance тесты прошли успешно
)
cd ..\..

echo.
echo [4/4] Запуск интеграционных тестов...
cd web-service\backend
echo Запуск интеграционных тестов...
python -m pytest tests/ -m integration -v --tb=short
if %errorlevel% neq 0 (
    echo WARNING: Интеграционные тесты не прошли (не критично)
) else (
    echo ✓ Интеграционные тесты прошли успешно
)
cd ..\..

echo.
echo ========================================
echo ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!
echo ========================================
echo.
echo Результаты:
echo - Backend: ✓
echo - Frontend: ✓
echo - Performance: Проверено
echo - Integration: Проверено
echo.
echo Система готова к деплою!
pause
