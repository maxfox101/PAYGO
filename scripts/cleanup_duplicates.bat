@echo off
echo ========================================
echo PayGo - Очистка дублирующихся файлов
echo ========================================
echo.

echo [1/7] Удаление дублирующейся папки PayGo...
if exist "PayGo" (
    rmdir /s /q "PayGo"
    echo ✓ Папка PayGo удалена (дубликат)
) else (
    echo - Папка PayGo не найдена
)

echo [2/7] Удаление нерелевантной папки Sql...
if exist "Sql" (
    rmdir /s /q "Sql"
    echo ✓ Папка Sql удалена
) else (
    echo - Папка Sql не найдена
)

echo [3/7] Удаление устаревшего README_local.md...
if exist "README_local.md" (
    del "README_local.md"
    echo ✓ README_local.md удален
) else (
    echo - README_local.md не найден
)

echo [4/7] Проверка результата...
echo.
echo Проверяем структуру проекта...
echo.
echo В корне должны остаться только:
dir /b
echo.
echo Основной проект остается в корне
echo.
echo ========================================
echo ОЧИСТКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Удалены дублирующиеся и нерелевантные папки:
echo - PayGo (дубликат)
echo - Sql (нерелевантная)
echo - README_local.md (устаревший)
echo.
echo Оставлена структура:
echo - web-service/ (основной)
echo - terminal/ (основной)
echo - config/ (основной)
echo - docs/ (основной)
echo - scripts/ (утилиты)
echo - .github/ (CI/CD)
echo - README.md (актуальный)
echo - docker-compose.yml (основной)
echo.
echo Теперь весь проект находится в корне
echo.
pause
