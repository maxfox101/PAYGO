@echo off
echo ========================================
echo PayGo - Очистка после переноса в PROJECT
echo ========================================
echo.

echo [1/5] Удаление дублирующейся папки PayGo...
if exist "PayGo" (
    rmdir /s /q "PayGo"
    echo ✓ Папка PayGo удалена (дубликат)
) else (
    echo - Папка PayGo не найдена
)

echo [2/5] Удаление нерелевантной папки Sql...
if exist "Sql" (
    rmdir /s /q "Sql"
    echo ✓ Папка Sql удалена
) else (
    echo - Папка Sql не найдена
)

echo [3/5] Удаление устаревшего README_local.md...
if exist "README_local.md" (
    del "README_local.md"
    echo ✓ README_local.md удален
) else (
    echo - README_local.md не найден
)

echo [4/5] Удаление временных файлов...
if exist "VERIFICATION_STEPS.md" (
    del "VERIFICATION_STEPS.md"
    echo ✓ VERIFICATION_STEPS.md удален
) else (
    echo - VERIFICATION_STEPS.md не найден
)

echo [5/5] Проверка результата...
echo.
echo Проверяем структуру проекта...
echo.
echo В корне должны остаться только:
dir /b
echo.
echo Основной проект находится в папке PROJECT/
echo.
echo ========================================
echo ОЧИСТКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Удалены дублирующиеся и нерелевантные файлы:
echo - PayGo (дубликат)
echo - Sql (нерелевантная)
echo - README_local.md (устаревший)
echo - VERIFICATION_STEPS.md (временный)
echo.
echo Оставлена структура:
echo - PROJECT/ (основной проект)
echo - scripts/ (утилиты для управления)
echo.
echo Теперь весь проект находится в папке PROJECT/
echo.
pause






