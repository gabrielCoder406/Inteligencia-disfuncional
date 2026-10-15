# Acceso a datos del club: todas las operaciones de la interfaz pasan por estas funciones,
# que ejecutan sentencias SQL propias (parametrizadas con %s para evitar inyección SQL).
import hashlib
from conexion_bd import consultar, ejecutar

def hash_clave(clave):
    """Las contraseñas se guardan como hash SHA-256 (igual que SHA2(clave, 256) en MySQL)."""
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()
