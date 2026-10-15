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

def traducir_error(e):
    """Convierte los códigos de error de MySQL en mensajes entendibles."""
    if e.errno == 1062:   # clave duplicada (PK o UNIQUE)
        if "correo" in e.msg:
            return "Ya existe un registro con ese correo electrónico."
        if "uq_pago_cuota" in e.msg:
            return "Esa cuota ya tiene un pago registrado."
        if "uq_cuota_periodo" in e.msg:
            return "Ya existe una cuota para ese jugador en ese período."
        return "Ya existe un registro con ese DNI / identificador."
    if e.errno in (1216, 1452):   # clave foránea inexistente
        return "Referencia inválida: la categoría, el jugador o la cuota no existen."
    if e.errno == 3819:   # restricción CHECK violada
        return f"Dato fuera de las reglas del sistema ({e.msg})."
    if e.errno == 1644:   # SIGNAL lanzado por un trigger
        return e.msg
    if e.errno in (1142, 1143):  # permiso denegado por el rol
        return "El usuario de la aplicación no tiene permiso para esa operación."
    return f"Error de base de datos ({e.errno}): {e.msg}"