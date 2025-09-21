# conexion.py
import mysql.connector


def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="fs",
        password="Gato7Sol",
        database="sistema_inventario",
    )
