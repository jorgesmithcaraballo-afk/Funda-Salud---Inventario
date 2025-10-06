@echo off
REM Script de compilación para Windows
REM Sistema de Inventario - Fundación Salud

echo ============================================================
echo 🔨 COMPILANDO EJECUTABLE PORTABLE - FundaSalud
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ❌ Error: main.py no encontrado
    echo Por favor ejecuta este script desde el directorio raíz del proyecto
    pause
    exit /b 1
)

REM Verificar que PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ⚠️  PyInstaller no encontrado, instalando...
    pip install pyinstaller>=6.0.0
)

REM Limpiar builds anteriores
echo 🧹 Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM Compilar con PyInstaller
echo 🔨 Compilando ejecutable...
pyinstaller build_portable.spec --clean --noconfirm

REM Verificar si la compilación fue exitosa
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ COMPILACIÓN EXITOSA
    echo ============================================================
    echo.
    
    REM Mostrar información del ejecutable
    if exist "dist\FundaSalud.exe" (
        echo 📦 Ejecutable creado: dist\FundaSalud.exe
        dir "dist\FundaSalud.exe"
    )
    
    echo.
    echo 📝 Notas importantes:
    echo   1. El ejecutable está en la carpeta 'dist\'
    echo   2. La primera vez que lo ejecutes, creará una carpeta 'data\' para la BD
    echo   3. Puedes distribuir el ejecutable sin dependencias adicionales
    echo   4. Algunos antivirus pueden marcarlo como sospechoso (falso positivo)
    echo.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ❌ ERROR EN LA COMPILACIÓN
    echo ============================================================
    echo Revisa los errores arriba para más detalles
    pause
    exit /b 1
)

pause
