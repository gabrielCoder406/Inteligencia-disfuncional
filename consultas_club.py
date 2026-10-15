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



# ------------------------------------------------ ALTAS ----------------------------------------------
def alta_jugador(datos, id_administrador):
    """Inserta un jugador nuevo. 'datos' ya viene validado por validaciones.validar_jugador.
    La contraseña inicial del portal de socios es 'socio123' (se guarda hasheada)."""
    ejecutar(
        "INSERT INTO JUGADOR (dni, nombre, apellido, fecha_nacimiento, correo_electronico, "
        "                     contrasena, es_federado, estado_deportivo, "
        "                     id_categoria, id_administrador) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (datos["dni"], datos["nombre"].strip(), datos["apellido"].strip(),
         datos["fecha_nacimiento"], datos["correo"].strip().lower(), hash_clave("socio123"),
         datos["es_federado"], datos["estado"], datos["id_categoria"], id_administrador))


def generar_cuotas_mes(mes, anio, dia_vencimiento=10):
    """Regla 2: genera la cuota del período para cada jugador habilitado
    que todavía no la tenga. Devuelve la cantidad de cuotas creadas."""
    filas, _ = ejecutar(
        "INSERT INTO CUOTA (mes, anio, monto, fecha_vencimiento, dni_jugador) "
        "SELECT %s, %s, c.monto_cuota, "
        "       MAKEDATE(%s, 1) + INTERVAL (%s - 1) MONTH + INTERVAL (%s - 1) DAY, j.dni "
        "FROM JUGADOR j JOIN CATEGORIA c ON c.id_categoria = j.id_categoria "
        "WHERE j.estado_deportivo <> 'Baja' "
        "  AND NOT EXISTS (SELECT 1 FROM CUOTA x "
        "                  WHERE x.dni_jugador = j.dni AND x.mes = %s AND x.anio = %s)",
        (mes, anio, anio, mes, dia_vencimiento, mes, anio))
    return filas


def registrar_pago(id_cuota, monto, medio_pago, id_administrador, comprobante=None):
    """Regla 4: registra el pago de una cuota. El trigger trg_pago_ai_saldar_cuota la pasa
    a 'Al día' y trg_pago_bi_validar rechaza montos insuficientes o cuotas ya saldadas.
    Devuelve el id del pago generado."""
    _, id_pago = ejecutar(
        "INSERT INTO PAGO (fecha, monto, medio_pago, comprobante, id_cuota, id_administrador) "
        "VALUES (CURDATE(), %s, %s, %s, %s, %s)",
        (monto, medio_pago, comprobante or None, id_cuota, id_administrador))
    return id_pago