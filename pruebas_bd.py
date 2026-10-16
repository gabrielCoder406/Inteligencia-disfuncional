# Pruebas de integración de la capa de datos (Hito 3).
# Ejecutar sobre la base recién cargada con:
#   script_ddl_club_deportivo_v5.sql -> script_roles_usuarios.sql -> script_datos_prueba.sql
# Uso: python pruebas_bd.py
import mysql.connector
import consultas_club as bd
import validaciones as val
from conexion_bd import ErrorBD, consultar, ejecutar
from config_bd import DB_CONFIG

resultados = []


def caso(codigo, descripcion, esperado, funcion):
    """Ejecuta un caso de prueba y registra si el resultado obtenido coincide con el esperado."""
    try:
        ok, obtenido = funcion()
    except ErrorBD as e:
        ok, obtenido = False, f"ErrorBD: {e}"
    resultados.append((codigo, descripcion, esperado, obtenido, "OK" if ok else "FALLA"))


def espera_error(funcion, texto):
    """Para los casos que deben ser rechazados: OK si la base devuelve el error esperado."""
    try:
        funcion()
        return False, "La operación fue aceptada"
    except ErrorBD as e:
        return texto.lower() in str(e).lower(), f"Rechazado: {e}"


def conectar_como(usuario, clave):
    cfg = dict(DB_CONFIG, user=usuario, password=clave)
    return mysql.connector.connect(**cfg)


NUEVO = {"dni": "47111222", "nombre": "Lucía", "apellido": "Bazán", "correo": "lucia.bazan@mail.com",
         "fecha_nacimiento": "2007-05-20", "es_federado": True, "estado": "Activo", "id_categoria": 10}

# --- Conexión y login -------------------------------------------------------------
caso("CP01", "Conexión con el usuario app_gpj", "Conecta y lee la versión",
     lambda: (True, "MySQL " + consultar("SELECT VERSION() AS v")[0]["v"]))
caso("CP02", "Login de administrador válido", "Sesión con rol admin",
     lambda: (lambda s: (s is not None and s["rol"] == "admin", f"rol={s and s['rol']}, {s and s['nombre']}"))(
         bd.iniciar_sesion("tesoreria@generalpazjunior.com", "admin123")))
caso("CP03", "Login de administrador con clave incorrecta", "Acceso denegado",
     lambda: (lambda s: (s is None, "Acceso denegado" if s is None else "Ingresó"))(
         bd.iniciar_sesion("tesoreria@generalpazjunior.com", "otra")))
caso("CP04", "Login de socio válido (DNI 35123456)", "Sesión con rol socio",
     lambda: (lambda s: (s is not None and s["rol"] == "socio", f"rol={s and s['rol']}, {s and s['nombre']}"))(
         bd.iniciar_sesion("35123456", "socio123")))
caso("CP05", "Login de socio dado de baja (DNI 48765432)", "Acceso denegado",
     lambda: (lambda s: (s is None, "Acceso denegado" if s is None else "Ingresó"))(
         bd.iniciar_sesion("48765432", "socio123")))

# --- Consultas --------------------------------------------------------------------
caso("CP06", "Consulta del padrón completo", "12 jugadores",
     lambda: (lambda f: (len(f) == 12, f"{len(f)} jugadores"))(bd.listar_jugadores()))
caso("CP07", "Consulta del padrón filtrando por 'Gómez'", "1 jugador (Lucas Gómez)",
     lambda: (lambda f: (len(f) == 1 and f[0]["dni"] == "53456789", f"{len(f)}: {f[0]['nombre_completo'] if f else '-'}"))(
         bd.listar_jugadores("Gómez")))
caso("CP08", "Consulta de deudores", "5 deudores, deuda total $36.000",
     lambda: (lambda f: (len(f) == 5 and sum(r["deuda_total"] for r in f) == 36000,
                         f"{len(f)} deudores, $" + f"{sum(r['deuda_total'] for r in f):,.0f}".replace(",", ".")))(
         bd.listar_deudores()))
caso("CP09", "Historial de pagos filtrado por septiembre 2026", "9 pagos",
     lambda: (lambda f: (len(f) == 9, f"{len(f)} pagos"))(bd.historial_pagos(mes=9, anio=2026)))

# --- Altas ------------------------------------------------------------------------
caso("CP10", "Validación de formulario con datos inválidos", "4 errores detectados en Python",
     lambda: (lambda e: (len(e) == 4, f"{len(e)} errores: {e[0]}"))(
         val.validar_jugador({"dni": "12.345", "nombre": "Ana1", "apellido": "Paz", "correo": "ana@",
                              "fecha_nacimiento": "31/02/2010", "estado": "Activo", "id_categoria": 1})))


def alta_valida():
    bd.alta_jugador(NUEVO, 1)
    j = bd.obtener_jugador("47111222")
    return j is not None, f"Insertado: {j['nombre_completo']} ({j['categoria']})" if j else "No aparece"


caso("CP11", "Alta de jugador válido", "Se inserta y aparece en el padrón", alta_valida)
caso("CP12", "Alta con DNI repetido", "Rechazado por PRIMARY KEY",
     lambda: espera_error(lambda: bd.alta_jugador(dict(NUEVO, correo="otro@mail.com"), 1), "DNI"))
caso("CP13", "Alta con correo repetido", "Rechazado por UNIQUE",
     lambda: espera_error(lambda: bd.alta_jugador(dict(NUEVO, dni="47111223"), 1), "correo"))
caso("CP14", "Alta con DNI no numérico (sin pasar por Python)", "Rechazado por CHECK ck_jugador_dni",
     lambda: espera_error(lambda: bd.alta_jugador(dict(NUEVO, dni="12AB", correo="x1@mail.com"), 1),
                          "ck_jugador_dni"))
caso("CP15", "Alta con categoría inexistente (id 999)", "Rechazado por FOREIGN KEY",
     lambda: espera_error(lambda: bd.alta_jugador(dict(NUEVO, dni="47111224", correo="x2@mail.com",
                                                       id_categoria=999), 1), "Referencia inválida"))

# --- Cuotas y pagos ---------------------------------------------------------------
caso("CP16", "Generar cuotas de noviembre 2026", "12 cuotas (excluye al jugador de baja)",
     lambda: (lambda n: (n == 12, f"{n} cuotas generadas"))(bd.generar_cuotas_mes(11, 2026)))
caso("CP17", "Generar otra vez noviembre 2026", "0 cuotas (no duplica)",
     lambda: (lambda n: (n == 0, f"{n} cuotas generadas"))(bd.generar_cuotas_mes(11, 2026)))


def pago_valido():
    cuota = bd.cuotas_pendientes("53456789")[0]
    id_pago = bd.registrar_pago(cuota["id_cuota"], cuota["monto"], "Efectivo", 1)
    estado = consultar("SELECT estado_pago FROM CUOTA WHERE id_cuota = %s", (cuota["id_cuota"],))[0]
    return estado["estado_pago"] == "Al día", f"Pago #{id_pago}; cuota {cuota['mes']:02d}/{cuota['anio']} -> {estado['estado_pago']}"


caso("CP18", "Registrar pago de cuota en mora (Lucas Gómez)", "Cuota pasa a 'Al día' (trigger)", pago_valido)
caso("CP19", "Registrar un segundo pago para la misma cuota", "Rechazado: cuota ya saldada",
     lambda: espera_error(lambda: bd.registrar_pago(
         consultar("SELECT id_cuota FROM CUOTA WHERE dni_jugador='53456789' AND mes=8 AND anio=2026")[0]["id_cuota"],
         4500, "Efectivo", 1), "ya se encuentra saldada"))
caso("CP20", "Pago con monto menor al de la cuota", "Rechazado por trigger",
     lambda: espera_error(lambda: bd.registrar_pago(bd.cuotas_pendientes("53456789")[0]["id_cuota"],
                                                    100, "Efectivo", 1), "menor al importe"))
caso("CP21", "Pago con medio de pago inválido ('Cheque')", "Rechazado por CHECK ck_pago_medio",
     lambda: espera_error(lambda: bd.registrar_pago(bd.cuotas_pendientes("53456789")[0]["id_cuota"],
                                                    4500, "Cheque", 1), "ck_pago_medio"))
caso("CP22", "Insertar cuota para un jugador dado de baja", "Rechazado por trigger",
     lambda: espera_error(lambda: ejecutar(
         "INSERT INTO CUOTA (mes, anio, monto, fecha_vencimiento, dni_jugador) "
         "VALUES (12, 2026, 5000, '2026-12-10', '48765432')"), "dado de baja"))

# --- Roles de acceso --------------------------------------------------------------
caso("CP23", "app_gpj intenta borrar un pago (DELETE)", "Denegado: rol sin DELETE",
     lambda: espera_error(lambda: ejecutar("DELETE FROM PAGO WHERE id_pago = 1"), "no tiene permiso"))


def lectura_tablas():
    con = conectar_como("consulta_gpj", "ConsultaGPJ#2026")
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM JUGADOR")
        cur.fetchall()
        return False, "Pudo leer la tabla"
    except mysql.connector.Error as e:
        return e.errno == 1142, f"Denegado (error {e.errno})"
    finally:
        con.close()


def lectura_vistas():
    con = conectar_como("consulta_gpj", "ConsultaGPJ#2026")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM v_deudores")
    n = cur.fetchone()[0]
    con.close()
    return True, f"Lee v_deudores ({n} filas, ya con noviembre generado)"


caso("CP24", "consulta_gpj lee la tabla JUGADOR", "Denegado: solo ve vistas", lectura_tablas)
caso("CP25", "consulta_gpj lee la vista v_deudores", "Permitido", lectura_vistas)

# --- Informe ----------------------------------------------------------------------
if __name__ == "__main__":
    for r in resultados:
        print(" | ".join(str(x) for x in r))
    ok = sum(1 for r in resultados if r[4] == "OK")
    print(f"\nResultado: {ok}/{len(resultados)} casos OK")
