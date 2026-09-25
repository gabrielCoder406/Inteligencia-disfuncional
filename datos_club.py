# Base de datos en memoria (Estructura simple de primer año)
users = {
    "admin": {"pass": "admin123", "role": "admin"},
    "12345678": {"pass": "socio123", "role": "socio", "nombre": "Juan", "apellido": "Pérez",
               "dni": "12345678", "email": "juan@club.com", "federado": "SI", 
               "categoria": "PRIMERA DIVISION", "estado": "🔴 En mora"}
}
socios = [users["12345678"]]
pagos = [{"dni": "12345678", "mes_anio": "08/2026", "monto": "$5000", "cat": "PRIMERA DIVISION", "fecha": "24/09/2026"}]

