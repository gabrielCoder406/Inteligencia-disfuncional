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
