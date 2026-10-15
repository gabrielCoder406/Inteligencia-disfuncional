# Capa de conexión: abre la conexión con MySQL y ejecuta sentencias SQL parametrizadas.
# Requiere: pip install mysql-connector-python
import mysql.connector
from mysql.connector import Error
from config_bd import DB_CONFIG


class ErrorBD(Exception):
    """Error de base de datos con un mensaje apto para mostrar al usuario."""


def obtener_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise ErrorBD(f"No se pudo conectar a la base de datos: {e.msg}") from e

