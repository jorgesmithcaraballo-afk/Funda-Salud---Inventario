import subprocess
import time
import mysql.connector
from mysql.connector import Error
import os
import sys

# Configuración de conexión
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "/mu5?p9-ci7F",
    "database": "inventario",  # opcional si solo quieres probar conexión
}

# Ruta a tu aplicación principal
APP_SCRIPT = "main.py"


def verificar_mysql():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Conexión a MySQL exitosa.")
            connection.close()
            return True
    except Error as e:
        print(f"❌ Error de conexión: {e}")
    return False


def iniciar_aplicacion():
    print("🚀 Iniciando aplicación...")
    subprocess.run([sys.executable, APP_SCRIPT])


def esperar_mysql(max_reintentos=10, intervalo=5):
    intentos = 0
    while intentos < max_reintentos:
        print(f"🔄 Verificando MySQL... (intento {intentos + 1})")
        if verificar_mysql():
            iniciar_aplicacion()
            return
        intentos += 1
        time.sleep(intervalo)
    print("❌ No se pudo conectar a MySQL después de varios intentos.")


if __name__ == "__main__":
    esperar_mysql()
