"""
Centralized strings for the application
"""

# Main application
APP_TITLE = "Sistema de Inventario - Fundación Salud"
APP_LOADING = "Iniciando configuración automática de MySQL..."
APP_DB_SUCCESS = "Base de datos MySQL ya configurada"

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
LOGIN_SUCCESS = "Login exitoso para usuario:"
LOGIN_FAILED = "Credenciales incorrectas para usuario:"

# Subir view (add products)
SUBIR_TITLE = "ACTUALIZAR INVENTARIO"
CONFIGURACION_TITLE = "CONFIGURACIÓN"

# Chat AI view
CHAT_TITLE = "Asistente IA - Inventario"
CHAT_STATUS_ACTIVE = "IA Activa 🟢"
CHAT_STATUS_BASIC = "IA Desconectada 🔴"
CHAT_INPUT_PLACEHOLDER = "Escribe el nombre del producto..."
CHAT_SEND_BUTTON = "Enviar "
CHAT_WELCOME = "¡Hola! Soy tu asistente de inventario"
CHAT_WELCOME_OPTIONS = "Selecciona una de las siguientes opciones para comenzar:"

# Database error view
DB_ERROR_TITLE = "Error de Base de Datos"
DB_ERROR_MAIN_MESSAGE = "No se pudo conectar a la base de datos MySQL."
DB_ERROR_REASONS = """Esto puede ocurrir si:
• MySQL no está instalado o ejecutándose
• La base de datos 'sistema_inventario' no existe
• El usuario 'fs' no tiene permisos"""

DB_ERROR_BUTTON_AUTO = "Configurar MySQL Automáticamente"
DB_ERROR_BUTTON_MANUAL = "Configurar Conexión Manualmente"
DB_ERROR_BUTTON_RETRY = "Reintentar Conexión"

# Progress messages
DB_PROGRESS_STARTING = "Iniciando configuración automática..."
DB_PROGRESS_MYSQL = "Configurando base de datos MySQL..."
DB_PROGRESS_SUCCESS = "¡Base de datos MySQL creada exitosamente!"
DB_SUCCESS_TITLE = "¡Configuración Exitosa!"
DB_SUCCESS_MESSAGE = """La base de datos MySQL se ha configurado correctamente."""

# Debug and log messages
DEBUG_LOGIN_HEADER = "LOGIN DEBUG:"
DEBUG_USER_INPUT = "   - Usuario ingresado: [{usuario}] (longitud: {len_usuario})"
DEBUG_PASS_INPUT = "   - Clave ingresada: [{password}] (longitud: {len_password})"
DEBUG_USERS_IN_DB = "   - Usuarios en BD: {users}"
DEBUG_QUERY_EXECUTED = "   - Consulta ejecutada: {query}"
DEBUG_QUERY_PARAMS = "   - Parámetros: usuario='{usuario}', clave='{password}'"
DEBUG_QUERY_RESULT = "   - Resultado: {result}"
DEBUG_BACK_NAVIGATION = "Regresando a vista: {view}"
DEBUG_BACK_ERROR = "Error regresando a vista anterior: {error}"

# LOGIN WINDOW
INICIAR_SESION = "Iniciar Sesión"
MOSTRAR_CONTRASEÑA = "Mostrar contraseña"
ACCEDER = "Acceder"

# Additional shared UI strings (without emojis)
SELECCIONAR = "Seleccionar"
SELECCIONA_UNA_CONSULTA = "Selecciona una consulta:"
RESPUESTA = "Respuesta:"
CONFIGURACION_DEL_SISTEMA = "Configuración del Sistema"
NUEVO_CODIGO_SUFFIX = "(Nuevo Codigo)"
BUSCAR_PLACEHOLDER = "Buscar..."
CARGANDO = "Cargando..."

# Login errors and validations
LOGIN_ERROR_EMPTY = "Ingresa usuario y contraseña"
LOGIN_ERROR_USERNAME_FORMAT = "El usuario solo puede contener letras y números"
LOGIN_ERROR_USERNAME_TOO_LONG = "El usuario no puede exceder 32 caracteres"
LOGIN_ERROR_PASSWORD_TOO_LONG = "La contraseña no puede exceder 128 caracteres"

# FILTRO WINDOW
FILTRO_TITLE = "GESTIÓN DE INVENTARIO"
FILTRO_NO_RESULTS = "No se encontraron coincidencias."
EXCEL_EXPORT_TITLE = "Exportar a Excel"
CODIGO = "Código"
DESCRIPCION = "Descripción"
E_INICIAL = "E. Inicial"
ENTRADAS = "Entradas"
SALIDAS = "Salidas"
E_FINAL = "E. Final"
CANTIDAD = "Cantidad"
COSTO = "Costo"
MONTO = "Monto"

# SUBIR WINDOW
SUBIR_TITLE = "ACTUALIZAR INVENTARIO"
SUBIR_CODE_PLACEHOLDER = "Código del producto"
SUBIR_DESCRIPTION_PLACEHOLDER = "Descripción del producto"
CATEGORIA = "Categoría del producto"
SUBIR_QUANTITY_PLACEHOLDER = "Cantidad del producto"
SUBIR_COST_PLACEHOLDER = "Costo del producto"
GUARDAR = "Guardar"

# CONFIGURACION WINDOW
USUARIOS = "Gestionar usuarios"
AGREGAR_USUARIO = "Agregar usuario"
CATEGORIAS = "Gestionar categorías"
ELIMINAR_PRODUCTOS = "Eliminar productos"
USUARIOS_TITULO = "Usuarios"
LISTA_USUARIOS = "Lista de usuarios"
NUEVO_USUARIO = "Nuevo usuario"
COMPLETAR_DATOS_NUEVO_USUARIO = "Complete los datos del nuevo usuario"
NOMBRE = "Nombre"
APELLIDO = "Apellido"
ID = "ID"
CONTRASENA = "Contraseña"
CONFIRMAR_CONTRASEÑA = "Confirmar contraseña"
# ASCII-safe alias to prevent import mismatches without tilde
CONFIRMAR_CONTRASENA = CONFIRMAR_CONTRASEÑA
TIPO = "Tipo"
ACCIONES = "Acciones"
EDITAR = "Editar"
ELIMINAR = "Eliminar"
USUARIO = "Usuario"
PROTEGIDO = "Protegido"
NO_ELIMINAR_ADMIN_PRINCIPAL = "No se puede eliminar el admin principal"
CONFIRMAR_ELIMINACION = "Confirmar eliminación"
USUARIO_ELIMINADO = "Usuario eliminado"
NO_SE_PUDO_ELIMINAR_USUARIO = "No se pudo eliminar el usuario (protegido o error)"
NUEVA_CONTRASEÑA = "Nueva contraseña"
TIPO_USUARIO = "Tipo de usuario"
CANCELAR = "Cancelar"
CERRAR = "Cerrar"
CONFIRMAR_ELIMINACION_DE_USUARIO = "Confirmar eliminación de usuario"
ESTA_ACCION_NO_PUEDE_SER_REVERTIDA = "Esta acción no puede ser revertida"
CATEGORIAS = "Categorías"
GESTIONA_Y_ORGANIZA = "Gestiona y organiza las categorías"
NUEVA_CATEGORIA = "Nueva categoría"
AGREGAR = "Agregar"
RENOMBRAR = "Renombrar"
