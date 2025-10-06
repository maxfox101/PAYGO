@echo off
echo ========================================
echo PayGo - НЕМЕДЛЕННАЯ РЕОРГАНИЗАЦИЯ
echo ========================================
echo.

echo [1] Переименование PROECT в PROJECT...
if exist "PROECT" (
    ren "PROECT" "PROJECT"
    echo ✓ PROECT переименован в PROJECT
) else (
    echo - PROECT не найден
)

echo [2] Перенос web-service...
if exist "web-service" (
    move "web-service" "PROJECT\"
    echo ✓ web-service перенесен
) else (
    echo - web-service не найден
)

echo [3] Перенос terminal...
if exist "terminal" (
    move "terminal" "PROJECT\"
    echo ✓ terminal перенесен
) else (
    echo - terminal не найден
)

echo [4] Перенос config...
if exist "config" (
    move "config" "PROJECT\"
    echo ✓ config перенесен
) else (
    echo - config не найден
)

echo [5] Перенос docs...
if exist "docs" (
    move "docs" "PROJECT\"
    echo ✓ docs перенесен
) else (
    echo - docs не найден
)

echo [6] Перенос .github...
if exist ".github" (
    move ".github" "PROJECT\"
    echo ✓ .github перенесен
) else (
    echo - .github не найден
)

echo [7] Перенос основных файлов...
if exist "README.md" (
    move "README.md" "PROJECT\"
    echo ✓ README.md перенесен
)
if exist "docker-compose.yml" (
    move "docker-compose.yml" "PROJECT\"
    echo ✓ docker-compose.yml перенесен
)
if exist "DOCKER_SETUP.md" (
    move "DOCKER_SETUP.md" "PROJECT\"
    echo ✓ DOCKER_SETUP.md перенесен
)

echo [8] Удаление дубликатов...
if exist "PayGo" (
    rmdir /s /q "PayGo"
    echo ✓ PayGo удален
)
if exist "Sql" (
    rmdir /s /q "Sql"
    echo ✓ Sql удален
)
if exist "README_local.md" (
    del "README_local.md"
    echo ✓ README_local.md удален
)
if exist "VERIFICATION_STEPS.md" (
    del "VERIFICATION_STEPS.md"
    echo ✓ VERIFICATION_STEPS.md удален
)
if exist "README_REORGANIZATION.md" (
    del "README_REORGANIZATION.md"
    echo ✓ README_REORGANIZATION.md удален
)

echo.
echo ========================================
echo ГОТОВО! Проверяем результат:
echo ========================================
dir
echo.
echo В папке PROJECT:
dir PROJECT
echo.
echo РЕОРГАНИЗАЦИЯ ЗАВЕРШЕНА!
echo Теперь работайте из папки PROJECT
pause
