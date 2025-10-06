@echo off
REM Script de instalación y configuración de MySQL para Windows
REM Sistema de Inventario - Fundación Salud

echo ============================================================
echo 🔧 CONFIGURACIÓN DE MYSQL PARA FUNDASALUD
echo ============================================================
echo.

REM Verificar si MySQL está instalado
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MySQL ya está instalado
    goto :configure_db
)

echo ⚠️  MySQL no está instalado en este sistema
echo.
echo Para instalar MySQL, tienes dos opciones:
echo.
echo OPCIÓN 1: Instalación Manual (Recomendado)
echo   1. Descarga MySQL Community Server desde:
echo      https://dev.mysql.com/downloads/mysql/
echo   2. Ejecuta el instalador
echo   3. Durante la instalación:
echo      - Selecciona "Developer Default"
echo      - Configura password root (anótalo)
echo   4. Vuelve a ejecutar este script
echo.
echo OPCIÓN 2: Instalación con Chocolatey (Automático)
echo   1. Abre PowerShell como Administrador
echo   2. Ejecuta: choco install mysql
echo   3. Vuelve a ejecutar este script
echo.
pause
exit /b 1

:configure_db
echo.
echo 🔧 Configurando base de datos...
echo.

REM Solicitar credenciales de root
set /p ROOT_PASSWORD="Ingresa la contraseña de root de MySQL: "

REM Crear base de datos y usuario
echo.
echo 📋 Creando base de datos 'sistema_inventario'...
mysql -u root -p%ROOT_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS sistema_inventario;" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: No se pudo conectar a MySQL
    echo Verifica que la contraseña sea correcta
    pause
    exit /b 1
)

echo ✅ Base de datos creada

echo 👤 Creando usuario 'fs'...
mysql -u root -p%ROOT_PASSWORD% -e "DROP USER IF EXISTS 'fs'@'localhost';" 2>nul
mysql -u root -p%ROOT_PASSWORD% -e "CREATE USER 'fs'@'localhost' IDENTIFIED BY 'Gato7Sol';"
mysql -u root -p%ROOT_PASSWORD% -e "GRANT ALL PRIVILEGES ON sistema_inventario.* TO 'fs'@'localhost';"
mysql -u root -p%ROOT_PASSWORD% -e "FLUSH PRIVILEGES;"

if %errorlevel% equ 0 (
    echo ✅ Usuario creado y permisos otorgados
) else (
    echo ❌ Error creando usuario
    pause
    exit /b 1
)

REM Importar estructura si existe
if exist "database\estructura_bd.sql" (
    echo 📊 Importando estructura de base de datos...
    mysql -u fs -pGato7Sol sistema_inventario < database\estructura_bd.sql
    if %errorlevel% equ 0 (
        echo ✅ Estructura importada correctamente
    ) else (
        echo ⚠️  Error importando estructura (puede ser normal si ya existe)
    )
)

echo.
echo ============================================================
echo ✅ CONFIGURACIÓN COMPLETADA
echo ============================================================
echo.
echo Detalles de conexión:
echo   Host: localhost
echo   Usuario: fs
echo   Contraseña: Gato7Sol
echo   Base de datos: sistema_inventario
echo.
echo Ahora puedes ejecutar FundaSalud.exe
echo.
echo ============================================================
pause
