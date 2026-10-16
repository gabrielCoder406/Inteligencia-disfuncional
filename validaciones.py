# Validaciones de los datos ingresados en la interfaz, antes de enviarlos a la base.
# Son la primera barrera; la segunda son las restricciones (CHECK, UNIQUE, FK) y los
# triggers del esquema. Cada función devuelve un mensaje de error o None si está todo bien.
import re
from datetime import date, datetime

ESTADOS_DEPORTIVOS = ("Activo", "Baja", "Lesionado")
MEDIOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta")


def validar_dni(dni):
    if not re.fullmatch(r"\d{7,8}", dni or ""):
        return "El DNI debe tener 7 u 8 dígitos, sin puntos."
    return None


def validar_texto(valor, campo):
    if not valor or not valor.strip():
        return f"{campo} es obligatorio."
    if len(valor) > 50:
        return f"{campo} admite hasta 50 caracteres."
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' ]+", valor.strip()):
        return f"{campo} solo puede contener letras y espacios."
    return None


def validar_correo(correo):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", correo or ""):
        return "El correo electrónico no tiene un formato válido."
    return None


def convertir_fecha(texto):
    """Acepta dd/mm/aaaa y devuelve un date, o None si es inválida."""
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        return None


def validar_fecha_nacimiento(texto):
    f = convertir_fecha(texto)
    if f is None:
        return "La fecha de nacimiento debe tener el formato dd/mm/aaaa."
    if f > date.today() or f.year < 1930:
        return "La fecha de nacimiento está fuera de rango."
    return None


def validar_monto(texto):
    try:
        monto = float(str(texto).replace(",", "."))
    except ValueError:
        return "El monto debe ser un número."
    if monto <= 0:
        return "El monto debe ser mayor a cero."
    return None


def validar_jugador(datos):
    """Valida el formulario de alta completo. Devuelve la lista de errores encontrados."""
    errores = [
        validar_dni(datos.get("dni")),
        validar_texto(datos.get("nombre"), "Nombre"),
        validar_texto(datos.get("apellido"), "Apellido"),
        validar_correo(datos.get("correo")),
        validar_fecha_nacimiento(datos.get("fecha_nacimiento")),
        None if datos.get("estado") in ESTADOS_DEPORTIVOS else "Estado deportivo inválido.",
        None if datos.get("id_categoria") else "Debe seleccionar una categoría.",
    ]
    return [e for e in errores if e]
