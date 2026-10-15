# Acceso a datos del club: todas las operaciones de la interfaz pasan por estas funciones,
# que ejecutan sentencias SQL propias (parametrizadas con %s para evitar inyección SQL).
import hashlib
from conexion_bd import consultar, ejecutar

def hash_clave(clave):
    """Las contraseñas se guardan como hash SHA-256 (igual que SHA2(clave, 256) en MySQL)."""
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


# ------------------------------------- INICIO DE SESIÓN -------------------------------------------
def iniciar_sesion(usuario, clave):
    """Administrador: ingresa con su correo. Socio: ingresa con su DNI.
    Devuelve un diccionario con los datos de la sesión,
    o None si las credenciales no coinciden."""
    if "@" in usuario:
        filas = consultar(
            "SELECT id_administrador, nombre, correo "
            "FROM ADMINISTRADOR WHERE correo = %s AND contrasena = %s",
            (usuario, hash_clave(clave)))
        return {"rol": "admin", **filas[0]} if filas else None
    filas = consultar(
        "SELECT dni, nombre, apellido "
        "FROM JUGADOR WHERE dni = %s AND contrasena = %s AND estado_deportivo <> 'Baja'",
        (usuario, hash_clave(clave)))
    return {"rol": "socio", **filas[0]} if filas else None



# --------------------------------------- CONSULTAS ------------------------------------------
def listar_categorias():
    return consultar(
        "SELECT id_categoria, nombre_categoria, monto_cuota FROM CATEGORIA ORDER BY id_categoria")


def listar_jugadores(busqueda=""):
    """Padrón general. Filtra por DNI o por nombre/apellido si se indica una búsqueda."""
    patron = f"%{busqueda.strip()}%"
    return consultar(
        "SELECT dni, nombre_completo, categoria, federado, estado_deportivo, "
        "       estado_cuenta, responsable "
        "FROM v_padron_jugadores "
        "WHERE dni LIKE %s OR nombre_completo LIKE %s "
        "ORDER BY nombre_completo",
        (patron, patron))


def obtener_jugador(dni):
    filas = consultar("SELECT * FROM v_padron_jugadores WHERE dni = %s", (dni,))
    return filas[0] if filas else None


def resumen_padron():
    return consultar(
        "SELECT COUNT(*) AS total, "
        "       SUM(estado_cuenta = 'Al día')  AS al_dia, "
        "       SUM(estado_cuenta = 'En mora') AS en_mora "
        "FROM v_padron_jugadores WHERE estado_deportivo <> 'Baja'")[0]


def cuotas_pendientes(dni):
    return consultar(
        "SELECT id_cuota, mes, anio, monto, fecha_vencimiento "
        "FROM CUOTA WHERE dni_jugador = %s AND estado_pago = 'En mora' "
        "ORDER BY anio, mes",
        (dni,))


def historial_pagos(dni=None, mes=None, anio=None):
    """Historial de pagos con filtros opcionales por jugador, mes y año."""
    sql = ("SELECT id_pago, fecha, dni, nombre_completo, periodo, monto, medio_pago, "
           "       comprobante, validado_por "
           "FROM v_historial_pagos WHERE 1 = 1")
    parametros = []
    if dni:
        sql += " AND dni = %s"
        parametros.append(dni)
    if mes:
        sql += " AND mes = %s"
        parametros.append(mes)
    if anio:
        sql += " AND anio = %s"
        parametros.append(anio)
    sql += " ORDER BY fecha DESC, id_pago DESC"
    return consultar(sql, tuple(parametros))


def listar_deudores():
    return consultar(
        "SELECT dni, nombre_completo, categoria, meses_adeudados, periodos, deuda_total "
        "FROM v_deudores ORDER BY deuda_total DESC")

