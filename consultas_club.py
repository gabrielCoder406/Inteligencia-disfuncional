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
