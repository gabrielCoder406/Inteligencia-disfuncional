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