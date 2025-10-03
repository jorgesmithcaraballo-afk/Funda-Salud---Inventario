"""
Centralized strings for the application
"""

# Main application
APP_TITLE = "Sistema de Inventario - Fundación Salud"
APP_LOADING = "🔄 Iniciando configuración automática de MySQL..."
APP_DB_SUCCESS = "✅ Base de datos MySQL ya configurada"

# Login view

LOGIN_TITLE = " Inicia Sesión"
LOGIN_USERNAME_PLACEHOLDER = "Nombre de usuario"
LOGIN_PASSWORD_PLACEHOLDER = "Contraseña"
LOGIN_SHOW_PASSWORD = "Mostrar contraseña"
LOGIN_BUTTON = "Acceder"

# Login messages
LOGIN_ERROR_TITLE = "Acceso denegado"
LOGIN_ERROR_MESSAGE = "Usuario o contraseña incorrectos"
LOGIN_ERROR_DB_TITLE = "Error de conexión"
LOGIN_ERROR_DB_MESSAGE = "No se pudo conectar a la base de datos:"
LOGIN_SUCCESS = "✅ Login exitoso para usuario:"
LOGIN_FAILED = "❌ Credenciales incorrectas para usuario:"

# Filtro view (main inventory)
FILTRO_TITLE = "GESTIÓN DE INVENTARIO"
FILTRO_NO_RESULTS = "No se encontraron coincidencias."

# Table headers
FILTRO_COLUMN_CODE = "Código"
FILTRO_COLUMN_DESCRIPTION = "Descripción"
FILTRO_COLUMN_INITIAL = "E. Inicial"
FILTRO_COLUMN_ENTRIES = "Entradas"
FILTRO_COLUMN_EXITS = "Salidas"
FILTRO_COLUMN_FINAL = "E. final"
FILTRO_SUBCOLUMN_QUANTITY = "Cant"
FILTRO_SUBCOLUMN_COST = "Costo"

# Excel export
FILTRO_EXCEL_TITLE = "Inventario"
FILTRO_EXCEL_HEADERS = [
    "Código", "Descripción",
    "E. Inicial Cant", "E. Inicial Costo", "E. Inicial Monto",
    "Entradas Cant", "Entradas Costo", "Entradas Monto",
    "Salidas Cant", "Salidas Costo", "Salidas Monto",
    "E. Final Cant", "E. Final Costo", "E. Final Monto"
]

# Subir view (add products)
SUBIR_TITLE = "AGREGAR TRABAJO"

# Chat AI view

CHAT_TITLE = "🤖 Asistente IA - Inventario"
CHAT_STATUS_ACTIVE = "🟢 IA Activa"
CHAT_STATUS_BASIC = "🟡 IA Básica"
CHAT_INPUT_PLACEHOLDER = "Escribe el nombre del producto..."
CHAT_SEND_BUTTON = "Enviar 📤"
CHAT_WELCOME = "¡Hola! 👋 Soy tu asistente de inventario"
CHAT_WELCOME_OPTIONS = "Selecciona una de las siguientes opciones para comenzar:"

# Database error view

DB_ERROR_TITLE = "⚠️ Error de Base de Datos"
DB_ERROR_MAIN_MESSAGE = "No se pudo conectar a la base de datos MySQL."
DB_ERROR_REASONS = """Esto puede ocurrir si:
• MySQL no está instalado o ejecutándose
• La base de datos 'sistema_inventario' no existe
• El usuario 'fs' no tiene permisos"""

DB_ERROR_BUTTON_AUTO = "🔧 Configurar MySQL Automáticamente"
DB_ERROR_BUTTON_MANUAL = "⚙️ Configurar Conexión Manualmente"
DB_ERROR_BUTTON_RETRY = "🔄 Reintentar Conexión"

# Progress messages
DB_PROGRESS_STARTING = "🔄 Iniciando configuración automática..."
DB_PROGRESS_MYSQL = "🗄️ Configurando base de datos MySQL..."
DB_PROGRESS_SUCCESS = "✅ ¡Base de datos MySQL creada exitosamente!"

DB_SUCCESS_TITLE = "¡Configuración Exitosa!"
DB_SUCCESS_MESSAGE = """La base de datos MySQL se ha configurado correctamente.

✅ Base de datos: sistema_inventario
✅ Usuario: fs@localhost
✅ Usuario administrador creado

Credenciales de acceso:
Usuario: admin
Contraseña: admin123

La aplicación se reiniciará automáticamente."""

# Navigation & buttons
BUTTON_HOME = "🏠"
BUTTON_CHAT = "💬"
BUTTON_BACK = "←"

# Configuration view
CONFIG_TITLE = "Configuración"

# Debug and log messages

DEBUG_LOGIN_HEADER = "🔍 LOGIN DEBUG:"
DEBUG_USER_INPUT = "   - Usuario ingresado: [{usuario}] (longitud: {len_usuario})"
DEBUG_PASS_INPUT = "   - Clave ingresada: [{password}] (longitud: {len_password})"
DEBUG_USERS_IN_DB = "   - Usuarios en BD: {users}"
DEBUG_QUERY_EXECUTED = "   - Consulta ejecutada: {query}"
DEBUG_QUERY_PARAMS = "   - Parámetros: usuario='{usuario}', clave='{password}'"
DEBUG_QUERY_RESULT = "   - Resultado: {result}"
DEBUG_BACK_NAVIGATION = "🔙 Regresando a vista: {view}"
DEBUG_BACK_ERROR = "❌ Error regresando a vista anterior: {error}"

# Hotkeys
HOTKEY_FULLSCREEN = "F11"
HOTKEY_EXIT_FULLSCREEN = "Escape"
