import tkinter as tk
from tkinter import ttk, messagebox
from datos_club import users
from paneles_club import PanelesMixin

class ClubApp(PanelesMixin, tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Club Atlético GPJ - Gestión de Socios")
        self.geometry("740x600"); self.configure(bg="#002147"); self.current_user = None
        style = ttk.Style(); style.theme_use('default')
        style.configure("TNotebook.Tab", background="#17a2b8", foreground="white", font=("Arial", 9, "bold"), padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", "#0056b3")], foreground=[("selected", "#FFFF00")])
        self.show_login()
        
    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def add_header(self, title):
        hdr = tk.Frame(self, bg="#002147"); hdr.pack(fill="x", pady=5, padx=10)
        try:
            self.logo = tk.PhotoImage(file="logo_club.gif.gif").subsample(5, 5)
            tk.Label(hdr, image=self.logo, bg="#002147").pack(side="left", padx=5)
        except Exception: pass
        sub = tk.Frame(hdr, bg="#002147"); sub.pack(side="left", padx=10)
        tk.Label(sub, text=f"⚽ {title}", font=("Helvetica", 13, "bold"), fg="#FFFF00", bg="#002147").pack(anchor="w")
        tk.Label(sub, text="🏆 Club Atlético GPJ • Pasión y Deporte • Fundado en 1925", font=("Helvetica", 8, "italic"), fg="#A0C4FF", bg="#002147").pack(anchor="w")
        if self.current_user:
            tk.Button(hdr, text="🔒 Cerrar Sesión", bg="#dc3545", fg="white", font=("Arial", 9, "bold"), command=self.show_login).pack(side="right", padx=5)

    def show_login(self):
        self.clear(); self.current_user = None; self.add_header("Acceso al Club GPJ")
        box = tk.Frame(self, bg="#E6F0FA", bd=3, relief="ridge"); box.pack(pady=40, ipadx=25, ipady=15)
        tk.Label(box, text="🔑 SISTEMA DE SOCIOS Y PAGOS", font=("Helvetica", 11, "bold"), bg="#E6F0FA", fg="#002147").grid(row=0, columnspan=2, pady=10)
        tk.Label(box, text="👤 Usuario (DNI / admin):", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=1, column=0, pady=5, sticky="e")
        u_ent = tk.Entry(box, width=18, font=("Arial", 10)); u_ent.grid(row=1, column=1, pady=5, padx=5)
        tk.Label(box, text="🔑 Contraseña:", font=("Arial", 9, "bold"), bg="#E6F0FA").grid(row=2, column=0, pady=5, sticky="e")
        p_ent = tk.Entry(box, show="*", width=18, font=("Arial", 10)); p_ent.grid(row=2, column=1, pady=5, padx=5)
        def login():
            u, p = u_ent.get().strip(), p_ent.get().strip()
            if u in users and users[u]["pass"] == p:
                self.current_user = users[u]
                self.show_admin() if users[u]["role"] == "admin" else self.show_socio()
            else: messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        tk.Button(box, text="🚀 Ingresar", bg="#002147", fg="white", font=("Arial", 10, "bold"), command=login, width=14).grid(row=3, columnspan=2, pady=15)

if __name__ == "__main__":
    app = ClubApp(); app.mainloop()
