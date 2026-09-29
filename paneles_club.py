import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from datos_club import users, socios, pagos
#pestaña visual de control de socios dentro del Perfil de Administrador.
class PanelesMixin:
    def show_admin(self):
        self.clear(); self.add_header("Panel de Administración")
        mf = tk.Frame(self, bg="#002147"); mf.pack(fill="both", expand=True, padx=15, pady=5)
        nb = ttk.Notebook(mf); nb.pack(fill="both", expand=True)
        t1 = tk.Frame(nb, bg="#E6F0FA"); nb.add(t1, text="👥 GESTIÓN DE SOCIOS")
        act = [s for s in socios if "Al día" in s["estado"]]; mora = [s for s in socios if "mora" in s["estado"]]
        tk.Label(t1, text=f"📊 Total Socios: {len(socios)}  |  🟢 Al Día: {len(act)}  |  🔴 En Mora: {len(mora)}", bg="#E6F0FA", font=("Helvetica", 10, "bold"), fg="#002147").pack(pady=6)
        tv = ttk.Treeview(t1, columns=("dni", "nom", "cat", "fed", "est"), show="headings", height=4)
        for c, h in [("dni","🏷️ DNI"), ("nom","👤 Nombre y Apellido"), ("cat","⚽ Categoría"), ("fed","🏅 Fed."), ("est","📌 Estado")]:
            tv.heading(c, text=h); tv.column(c, width=120, anchor="center")
        tv.pack(fill="x", padx=10)
        for s in socios: tv.insert("", "end", values=(s["dni"], f"{s['nombre']} {s['apellido']}", s["categoria"], s["federado"], s["estado"]))
        f_add = tk.LabelFrame(t1, text=" ➕ Registrar Nuevo Socio ", bg="#E6F0FA", font=("Helvetica", 9, "bold"), fg="#002147"); f_add.pack(fill="x", padx=10, pady=6)
        entries = {}
        for lbl, r, c in [("DNI", 0, 0), ("Nombre", 0, 2), ("Apellido", 1, 0), ("Email", 1, 2)]:
            tk.Label(f_add, text=f"{lbl}:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=r, column=c, padx=3, pady=2, sticky="e")
            e = tk.Entry(f_add, width=15); e.grid(row=r, column=c+1, padx=3, pady=2); entries[lbl] = e
        tk.Label(f_add, text="Federado:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=2, column=0, sticky="e")
        fed_cb = ttk.Combobox(f_add, values=["SI", "NO"], width=12, state="readonly"); fed_cb.grid(row=2, column=1); fed_cb.set("NO")
        tk.Label(f_add, text="Categoría:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=2, column=2, sticky="e")
        cats = ["SUB-13", "SUB-15", "SUB-17", "PRIMERA DIVISION", "ESCUELITA DE FUTBOL", "SOCIO RECREATIVO"]
        cat_cb = ttk.Combobox(f_add, values=cats, width=16, state="readonly"); cat_cb.grid(row=2, column=3); cat_cb.set("PRIMERA DIVISION")
                def add_socio():
            dni, nom, ape, eml = entries["DNI"].get().strip(), entries["Nombre"].get().strip(), entries["Apellido"].get().strip(), entries["Email"].get().strip()
            if not (dni and nom and ape): return messagebox.showerror("Error", "DNI, Nombre y Apellido obligatorios")
            s = {"dni": dni, "pass": "socio123", "role": "socio", "nombre": nom, "apellido": ape, "email": eml, "federado": fed_cb.get(), "categoria": cat_cb.get(), "estado": "🟢 Al día"}
            socios.append(s); users[dni] = s
            messagebox.showinfo("Éxito", f"¡Socio Registrado!\nEmail: {eml}\nContraseña genérica: socio123"); self.show_admin()
        tk.Button(f_add, text="💾 Guardar Socio", bg="#002147", fg="white", font=("Arial", 9, "bold"), command=add_socio).grid(row=3, columnspan=4, pady=5)

        t2 = tk.Frame(nb, bg="#E6F0FA"); nb.add(t2, text="💳 COBROS E HISTORIAL")
        f_pago = tk.LabelFrame(t2, text=" 💵 Registrar Cobro de Cuota ", bg="#E6F0FA", font=("Helvetica", 9, "bold"), fg="#002147"); f_pago.pack(fill="x", padx=10, pady=6)
        tk.Label(f_pago, text="👤 DNI Socio:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=0, column=0, padx=4, pady=3, sticky="e")
        s_cb = ttk.Combobox(f_pago, values=[s["dni"] for s in socios], width=12, state="readonly"); s_cb.grid(row=0, column=1)
        tk.Label(f_pago, text="📅 Mes/Año:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=0, column=2, padx=4, pady=3, sticky="e")
        ma_e = tk.Entry(f_pago, width=10); ma_e.grid(row=0, column=3); ma_e.insert(0, "09/2026")
        tk.Label(f_pago, text="💰 Monto ($):", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=1, column=0, padx=4, pady=3, sticky="e")
        m_e = tk.Entry(f_pago, width=12); m_e.grid(row=1, column=1); m_e.insert(0, "5000")