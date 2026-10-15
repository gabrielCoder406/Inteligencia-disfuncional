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


def consultar(sql, parametros=()):
    """Ejecuta un SELECT y devuelve una lista de diccionarios (columna -> valor)."""
    con = obtener_conexion()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, parametros)
        return cur.fetchall()
    except Error as e:
        raise ErrorBD(traducir_error(e)) from e
    finally:
        con.close()


def ejecutar(sql, parametros=()):
    """Ejecuta un INSERT/UPDATE dentro de una transacción.
    Devuelve (filas_afectadas, ultimo_id). Si algo falla, deshace los cambios."""
    con = obtener_conexion()
    try:
        cur = con.cursor()
        cur.execute(sql, parametros)
        con.commit()
        return cur.rowcount, cur.lastrowid
    except Error as e:
        con.rollback()
        raise ErrorBD(traducir_error(e)) from e
    finally:
        con.close()

