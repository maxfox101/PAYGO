@echo off
echo ========================================
echo PayGo - Перенос файлов в папку PROJECT
echo ========================================
echo.

echo [1/8] Создание папки PROJECT...
if not exist "PROJECT" (
    mkdir "PROJECT"
    echo ✓ Папка PROJECT создана
) else (
    echo - Папка PROJECT уже существует
)

echo [2/8] Перенос web-service...
if exist "web-service" (
    move "web-service" "PROJECT\"
    echo ✓ web-service перенесен в PROJECT
) else (
    echo - web-service не найден
)

echo [3/8] Перенос terminal...
if exist "terminal" (
    move "terminal" "PROJECT\"
    echo ✓ terminal перенесен в PROJECT
) else (
    echo - terminal не найден
)

echo [4/8] Перенос config...
if exist "config" (
    move "config" "PROJECT\"
    echo ✓ config перенесен в PROJECT
) else (
    echo - config не найден
)

echo [5/8] Перенос docs...
if exist "docs" (
    move "docs" "PROJECT\"
    echo ✓ docs перенесен в PROJECT
) else (
    echo - docs не найден
)

echo [6/8] Перенос .github...
if exist ".github" (
    move ".github" "PROJECT\"
    echo ✓ .github перенесен в PROJECT
) else (
    echo - .github не найден
)

echo [7/8] Перенос основных файлов...
if exist "README.md" (
    move "README.md" "PROJECT\"
    echo ✓ README.md перенесен в PROJECT
) else (
    echo - README.md не найден
)

if exist "docker-compose.yml" (
    move "docker-compose.yml" "PROJECT\"
    echo ✓ docker-compose.yml перенесен в PROJECT
) else (
    echo - docker-compose.yml не найден
)

if exist "DOCKER_SETUP.md" (
    move "DOCKER_SETUP.md" "PROJECT\"
    echo ✓ DOCKER_SETUP.md перенесен в PROJECT
) else (
    echo - DOCKER_SETUP.md не найден
)

echo [8/8] Проверка результата...
echo.
echo Проверяем структуру проекта...
echo.
echo В корне должны остаться только:
dir /b
echo.
echo Основной проект теперь находится в папке PROJECT/
echo.
echo ========================================
echo ПЕРЕНОС ЗАВЕРШЕН!
echo ========================================
echo.
echo Перенесены в PROJECT:
echo - web-service/ (веб-сервис)
echo - terminal/ (терминальное ПО)
echo - config/ (конфигурации)
echo - docs/ (документация)
echo - .github/ (CI/CD)
echo - README.md (документация)
echo - docker-compose.yml (Docker конфигурация)
echo - DOCKER_SETUP.md (инструкции по Docker)
echo.
echo Оставлены в корне:
echo - scripts/ (утилиты для управления)
echo - PROJECT/ (основной проект)
echo.
echo Теперь весь проект находится в папке PROJECT/
echo.
pause






