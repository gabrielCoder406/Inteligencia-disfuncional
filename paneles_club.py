import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import consultas_club as bd
import validaciones as val
from conexion_bd import ErrorBD

# Versión 4 (Hito 3): todas las grillas se cargan con SELECT y los formularios hacen INSERT
# a través de consultas_club.py. Ya no se usa datos_club.py.
BG = "#E6F0FA"; AZUL = "#002147"
MESES = ["Todos", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


def pesos(m):
    """5500 -> '$5.500,00' (formato argentino)."""
    return "$" + f"{float(m):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ddmmaaaa(f):
    return f.strftime("%d/%m/%Y") if f else ""


class PanelesMixin:
    # ------------------------------------------------------------------ utilidades
    def _tabla(self, padre, columnas, height=5):
        """Crea un Treeview con barra de desplazamiento. columnas = [(id, título, ancho), ...]"""
        marco = tk.Frame(padre, bg=BG); marco.pack(fill="both", expand=True, padx=10, pady=3)
        tv = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", height=height)
        for c, h, w in columnas:
            tv.heading(c, text=h); tv.column(c, width=w, anchor="center")
        sb = ttk.Scrollbar(marco, orient="vertical", command=tv.yview); tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
        tv.tag_configure("mora", foreground="#c82333")          # filas en mora en rojo
        return tv

    def _etiqueta(self, padre, texto, fila, col):
        tk.Label(padre, text=texto, font=("Arial", 9, "bold"), bg=BG).grid(row=fila, column=col, padx=3, pady=2, sticky="e")

    def _error_bd(self, e):
        messagebox.showerror("Base de datos", str(e))

    # ------------------------------------------------------------------ ADMINISTRADOR
    def show_admin(self, pestana=0):
        self.clear(); self.add_header(f"Panel de Administración - {self.current_user['nombre']}")
        mf = tk.Frame(self, bg=AZUL); mf.pack(fill="both", expand=True, padx=15, pady=5)
        self.nb = ttk.Notebook(mf); self.nb.pack(fill="both", expand=True)
        try:
            self._tab_padron(); self._tab_cobros(); self._tab_deudores()
        except ErrorBD as e:
            return self._error_bd(e)
        self.nb.select(pestana)

    def _recargar(self):
        """Vuelve a consultar la base y redibuja el panel en la misma pestaña."""
        self.show_admin(self.nb.index("current"))

    # --- Pestaña 1: padrón (CONSULTA) y alta de socios (ALTA) ---------------------------
    def _tab_padron(self):
        t1 = tk.Frame(self.nb, bg=BG); self.nb.add(t1, text="👥 PADRÓN Y ALTAS")
        r = bd.resumen_padron()
        tk.Label(t1, text=f"📊 Socios habilitados: {r['total']}  |  🟢 Al Día: {r['al_dia']}  |  🔴 En Mora: {r['en_mora']}",
                 bg=BG, font=("Helvetica", 10, "bold"), fg=AZUL).pack(pady=6)

        f_bus = tk.Frame(t1, bg=BG); f_bus.pack(fill="x", padx=10)
        tk.Label(f_bus, text="🔍 Buscar por DNI o nombre:", font=("Arial", 9, "bold"), bg=BG).pack(side="left")
        e_bus = tk.Entry(f_bus, width=25); e_bus.pack(side="left", padx=5)
        tv = self._tabla(t1, [("dni", "🏷️ DNI", 80), ("nom", "👤 Nombre y Apellido", 150), ("cat", "⚽ Categoría", 130),
                              ("fed", "🏅 Fed.", 50), ("dep", "🩺 Estado Dep.", 95), ("cta", "📌 Cuenta", 80),
                              ("resp", "🗂️ Responsable", 140)], height=7)

        def cargar(busqueda=""):
            tv.delete(*tv.get_children())
            try:
                for j in bd.listar_jugadores(busqueda):          # SELECT ... FROM v_padron_jugadores
                    mora = j["estado_cuenta"] == "En mora"
                    tv.insert("", "end", tags=("mora",) if mora else (),
                              values=(j["dni"], j["nombre_completo"], j["categoria"], j["federado"],
                                      j["estado_deportivo"], ("🔴 " if mora else "🟢 ") + j["estado_cuenta"], j["responsable"]))
            except ErrorBD as e:
                self._error_bd(e)
        tk.Button(f_bus, text="Buscar", bg=AZUL, fg="white", font=("Arial", 8, "bold"), command=lambda: cargar(e_bus.get())).pack(side="left")
        tk.Button(f_bus, text="Ver todos", bg="#6c757d", fg="white", font=("Arial", 8, "bold"),
                  command=lambda: (e_bus.delete(0, "end"), cargar())).pack(side="left", padx=4)
        e_bus.bind("<Return>", lambda e: cargar(e_bus.get()))
        cargar()

        f_add = tk.LabelFrame(t1, text=" ➕ Registrar Nuevo Socio ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL)
        f_add.pack(fill="x", padx=10, pady=6)
        entries = {}
        for lbl, r_, c in [("DNI", 0, 0), ("Nombre", 0, 2), ("Apellido", 0, 4), ("Email", 1, 0), ("Fecha Nac. (dd/mm/aaaa)", 1, 2)]:
            self._etiqueta(f_add, f"{lbl}:", r_, c)
            e = tk.Entry(f_add, width=22 if lbl == "Email" else 15); e.grid(row=r_, column=c + 1, padx=3, pady=2, sticky="w"); entries[lbl] = e
        self._etiqueta(f_add, "Federado:", 2, 0)
        fed_cb = ttk.Combobox(f_add, values=["SI", "NO"], width=12, state="readonly"); fed_cb.grid(row=2, column=1, sticky="w"); fed_cb.set("NO")
        self._etiqueta(f_add, "Categoría:", 2, 2)
        categorias = {c["nombre_categoria"]: c["id_categoria"] for c in bd.listar_categorias()}   # SELECT ... FROM CATEGORIA
        cat_cb = ttk.Combobox(f_add, values=list(categorias), width=18, state="readonly"); cat_cb.grid(row=2, column=3, sticky="w")
        self._etiqueta(f_add, "Estado Dep.:", 2, 4)
        est_cb = ttk.Combobox(f_add, values=["Activo", "Lesionado"], width=12, state="readonly"); est_cb.grid(row=2, column=5, sticky="w"); est_cb.set("Activo")

        def add_socio():
            datos = {"dni": entries["DNI"].get().strip(),
                     "nombre": entries["Nombre"].get().strip(),
                     "apellido": entries["Apellido"].get().strip(),
                     "correo": entries["Email"].get().strip(),
                     "fecha_nacimiento": entries["Fecha Nac. (dd/mm/aaaa)"].get().strip(),
                     "es_federado": fed_cb.get() == "SI",
                     "estado": est_cb.get(),
                     "id_categoria": categorias.get(cat_cb.get())}
            errores = val.validar_jugador(datos)          # 1ra barrera: validaciones en Python
            if errores:
                return messagebox.showerror("Datos inválidos", "\n".join(errores))
            datos["fecha_nacimiento"] = val.convertir_fecha(datos["fecha_nacimiento"])
            try:
                bd.alta_jugador(datos, self.current_user["id_administrador"])   # INSERT INTO JUGADOR
            except ErrorBD as e:                          # 2da barrera: restricciones de la base
                return self._error_bd(e)
            messagebox.showinfo("Éxito", f"¡Socio registrado!\n{datos['nombre']} {datos['apellido']} - "
                                         f"DNI {datos['dni']}\nContraseña inicial del portal: socio123")
            self._recargar()
        tk.Button(f_add, text="💾 Guardar Socio", bg=AZUL, fg="white", font=("Arial", 9, "bold"), command=add_socio).grid(row=3, columnspan=6, pady=5)

    # --- Pestaña 2: registro de cobros (ALTA de PAGO) e historial (CONSULTA) -------------
    def _tab_cobros(self):
        t2 = tk.Frame(self.nb, bg=BG); self.nb.add(t2, text="💳 COBROS E HISTORIAL")
        f_pago = tk.LabelFrame(t2, text=" 💵 Registrar Cobro de Cuota ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL)
        f_pago.pack(fill="x", padx=10, pady=6)
        socios = {f"{j['dni']} - {j['nombre_completo']}": j["dni"] for j in bd.listar_jugadores() if j["estado_cuenta"] == "En mora"}
        self._etiqueta(f_pago, "👤 Socio en mora:", 0, 0)
        s_cb = ttk.Combobox(f_pago, values=list(socios), width=26, state="readonly"); s_cb.grid(row=0, column=1, sticky="w")
        self._etiqueta(f_pago, "🗓️ Cuota pendiente:", 0, 2)
        c_cb = ttk.Combobox(f_pago, width=30, state="readonly"); c_cb.grid(row=0, column=3, sticky="w")
        self._etiqueta(f_pago, "💰 Monto ($):", 1, 0)
        m_e = tk.Entry(f_pago, width=12); m_e.grid(row=1, column=1, sticky="w")
        self._etiqueta(f_pago, "💳 Medio de pago:", 1, 2)
        medio_cb = ttk.Combobox(f_pago, values=list(val.MEDIOS_PAGO), width=15, state="readonly"); medio_cb.grid(row=1, column=3, sticky="w"); medio_cb.set("Efectivo")
        self._etiqueta(f_pago, "🧾 Comprobante (opcional):", 2, 0)
        comp_e = tk.Entry(f_pago, width=30); comp_e.grid(row=2, column=1, sticky="w")
        cuotas = {}

        def al_elegir_socio(_):
            cuotas.clear()
            for c in bd.cuotas_pendientes(socios[s_cb.get()]):      # SELECT ... FROM CUOTA WHERE estado 'En mora'
                cuotas[f"{c['mes']:02d}/{c['anio']} - {pesos(c['monto'])} (vto. {ddmmaaaa(c['fecha_vencimiento'])})"] = c
            c_cb.configure(values=list(cuotas)); c_cb.set(next(iter(cuotas), ""))
            al_elegir_cuota(None)

        def al_elegir_cuota(_):
            m_e.delete(0, "end")
            if c_cb.get(): m_e.insert(0, f"{cuotas[c_cb.get()]['monto']:.2f}")
        s_cb.bind("<<ComboboxSelected>>", al_elegir_socio); c_cb.bind("<<ComboboxSelected>>", al_elegir_cuota)

        def reg_cobro():
            if not s_cb.get() or not c_cb.get(): return messagebox.showerror("Error", "Seleccione el socio y la cuota")
            error = val.validar_monto(m_e.get())
            if error: return messagebox.showerror("Error", error)
            cuota = cuotas[c_cb.get()]
            try:
                id_pago = bd.registrar_pago(cuota["id_cuota"], m_e.get().replace(",", "."), medio_cb.get(),
                                            self.current_user["id_administrador"], comp_e.get().strip())   # INSERT INTO PAGO
            except ErrorBD as e:
                return self._error_bd(e)
            messagebox.showinfo("Éxito", f"Cobro #{id_pago} registrado el {date.today():%d/%m/%Y}.\nLa cuota {cuota['mes']:02d}/{cuota['anio']} quedó 'Al día'.")
            self._recargar()
        tk.Button(f_pago, text="✅ Registrar Cobro", bg="#28a745", fg="white", font=("Arial", 9, "bold"), command=reg_cobro).grid(row=2, column=2, columnspan=2, pady=4)

        tk.Label(t2, text="📋 Historial General de Pagos", font=("Helvetica", 10, "bold"), bg=BG, fg=AZUL).pack(pady=3)
        f_fil = tk.Frame(t2, bg=BG); f_fil.pack(fill="x", padx=10)
        tk.Label(f_fil, text="Mes:", font=("Arial", 9, "bold"), bg=BG).pack(side="left")
        mes_cb = ttk.Combobox(f_fil, values=MESES, width=6, state="readonly"); mes_cb.pack(side="left", padx=3); mes_cb.set("Todos")
        tk.Label(f_fil, text="Año:", font=("Arial", 9, "bold"), bg=BG).pack(side="left")
        anio_e = tk.Entry(f_fil, width=6); anio_e.pack(side="left", padx=3)
        tv_p = self._tabla(t2, [("id", "ID", 32), ("fecha", "📅 Fecha", 88), ("soc", "👤 Socio", 200), ("per", "🗓️ Período", 68),
                                ("monto", "💰 Monto", 85), ("medio", "💳 Medio", 95), ("comp", "🧾 Comprobante", 172),
                                ("val", "✔️ Validó", 140)], height=7)

        def cargar_historial():
            mes = None if mes_cb.get() == "Todos" else int(mes_cb.get())
            anio = int(anio_e.get()) if anio_e.get().strip().isdigit() else None
            tv_p.delete(*tv_p.get_children())
            for p in bd.historial_pagos(mes=mes, anio=anio):             # SELECT ... FROM v_historial_pagos
                tv_p.insert("", "end", values=(p["id_pago"], ddmmaaaa(p["fecha"]), f"{p['nombre_completo']} ({p['dni']})",
                                               p["periodo"], pesos(p["monto"]), p["medio_pago"], p["comprobante"] or "-", p["validado_por"]))
        tk.Button(f_fil, text="🔍 Aplicar Filtro", bg=AZUL, fg="white", font=("Arial", 8, "bold"), command=cargar_historial).pack(side="left", padx=5)
        cargar_historial()

    # --- Pestaña 3: deudores (CONSULTA) y generación mensual de cuotas (ALTA) -----------
    def _tab_deudores(self):
        t3 = tk.Frame(self.nb, bg=BG); self.nb.add(t3, text="🔴 SOCIOS EN MORA")
        tk.Label(t3, text="INFORME DE DEUDA Y MOROSIDAD", font=("Helvetica", 10, "bold"), bg=BG, fg="#dc3545").pack(pady=6)
        tv = self._tabla(t3, [("dni", "🏷️ DNI", 85), ("nom", "👤 Nombre y Apellido", 160), ("cat", "⚽ Categoría", 130),
                              ("cant", "Meses", 55), ("per", "🗓️ Períodos adeudados", 210), ("deuda", "💰 Deuda Total", 110)], height=8)
        deudores = bd.listar_deudores()                                  # SELECT ... FROM v_deudores
        for d in deudores:
            tv.insert("", "end", tags=("mora",), values=(d["dni"], d["nombre_completo"], d["categoria"], d["meses_adeudados"], d["periodos"], pesos(d["deuda_total"])))
        total = sum(d["deuda_total"] for d in deudores)
        tk.Label(t3, text=f"Total de jugadores en mora: {len(deudores)}  |  Deuda acumulada: {pesos(total)}",
                 font=("Arial", 9, "bold"), bg=BG, fg="#dc3545").pack(anchor="w", padx=12, pady=3)

        f_gen = tk.LabelFrame(t3, text=" 🗓️ Generar Cuotas del Mes (regla de negocio 2) ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL)
        f_gen.pack(fill="x", padx=10, pady=6)
        hoy = date.today()
        self._etiqueta(f_gen, "Mes:", 0, 0)
        mes_cb = ttk.Combobox(f_gen, values=MESES[1:], width=5, state="readonly"); mes_cb.grid(row=0, column=1); mes_cb.set(f"{hoy.month:02d}")
        self._etiqueta(f_gen, "Año:", 0, 2)
        anio_e = tk.Entry(f_gen, width=6); anio_e.grid(row=0, column=3); anio_e.insert(0, str(hoy.year))
        self._etiqueta(f_gen, "Vence el día:", 0, 4)
        dia_e = tk.Entry(f_gen, width=4); dia_e.grid(row=0, column=5); dia_e.insert(0, "10")

        def generar():
            if not (anio_e.get().isdigit() and dia_e.get().isdigit() and 1 <= int(dia_e.get()) <= 28):
                return messagebox.showerror("Error", "Año numérico y día de vencimiento entre 1 y 28")
            try:
                n = bd.generar_cuotas_mes(int(mes_cb.get()), int(anio_e.get()), int(dia_e.get()))   # INSERT ... SELECT
            except ErrorBD as e:
                return self._error_bd(e)
            messagebox.showinfo("Cuotas", f"Se generaron {n} cuotas para {mes_cb.get()}/{anio_e.get()}." if n else "Ese período ya estaba generado.")
            self._recargar()
        tk.Button(f_gen, text="⚙️ Generar", bg=AZUL, fg="white", font=("Arial", 9, "bold"), command=generar).grid(row=0, column=6, padx=10)

    # ------------------------------------------------------------------ SOCIO (solo consulta)
    def show_socio(self):
        self.clear()
        try:
            u = bd.obtener_jugador(self.current_user["dni"])                 # SELECT ... FROM v_padron_jugadores
            pendientes = bd.cuotas_pendientes(u["dni"])
            pagos = bd.historial_pagos(dni=u["dni"])
        except ErrorBD as e:
            return self._error_bd(e)
        self.add_header(f"Portal Socio: {u['nombre_completo']}")
        card = tk.Frame(self, bg=BG, bd=3, relief="ridge"); card.pack(pady=8, padx=15, fill="both", expand=True)
        f_info = tk.LabelFrame(card, text=" 👤 Datos Personales y Ficha ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL); f_info.pack(fill="x", padx=12, pady=6)
        cond = "🔴 En mora" if u["estado_cuenta"] == "En mora" else "🟢 Al día"
        info_txt = (f"🏷️ DNI: {u['dni']}  |  👤 Socio: {u['nombre_completo']}  |  ✉️ Email: {u['correo_electronico']}\n"
                    f"🏅 Federado: {u['federado']}  |  ⚽ Categoría: {u['categoria']}  |  🩺 Estado: {u['estado_deportivo']}  |  📌 Condición de pago: {cond}")
        tk.Label(f_info, text=info_txt, bg=BG, font=("Arial", 9, "bold"), fg=AZUL, justify="center").pack(pady=5)

        f_deuda = tk.LabelFrame(card, text=" 🔴 Cuotas Pendientes ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL); f_deuda.pack(fill="both", expand=True, padx=12, pady=6)
        tv_d = self._tabla(f_deuda, [("per", "🗓️ Período", 120), ("monto", "💰 Importe", 120), ("venc", "📅 Vencimiento", 120)], height=3)
        for c in pendientes:
            tv_d.insert("", "end", values=(f"{c['mes']:02d}/{c['anio']}", pesos(c["monto"]), ddmmaaaa(c["fecha_vencimiento"])))
        tk.Label(f_deuda, text=f"Deuda total: {pesos(sum(c['monto'] for c in pendientes))}  •  Para abonar, acercate a Tesorería con tu comprobante.",
                 bg=BG, font=("Arial", 8, "bold"), fg="#0056b3").pack(pady=2)

        f_pagos = tk.LabelFrame(card, text=" 📋 Historial de Mis Pagos ", bg=BG, font=("Helvetica", 9, "bold"), fg=AZUL); f_pagos.pack(fill="both", expand=True, padx=12, pady=6)
        tv = self._tabla(f_pagos, [("fecha", "📅 Fecha Pago", 110), ("per", "🗓️ Período", 100), ("monto", "💰 Monto Abonado", 120),
                                   ("medio", "💳 Medio", 110), ("comp", "🧾 Comprobante", 200)], height=4)
        for p in pagos:
            tv.insert("", "end", values=(ddmmaaaa(p["fecha"]), p["periodo"], pesos(p["monto"]), p["medio_pago"], p["comprobante"] or "-"))
