import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class ClubLogoCanvas(tk.Canvas):
    """
    Un componente Canvas personalizado que dibuja el escudo oficial de General Paz Junior de manera vectorial.
    Sirve como alternativa elegante de alta resolución si 'logo_club.gif' no está disponible.
    """
    def __init__(self, parent, size=150, **kwargs):
        kwargs.setdefault('width', size)
        kwargs.setdefault('height', size)
        kwargs.setdefault('bg', parent.cget('bg') if 'bg' in parent.keys() else '#F8F9FA')
        kwargs.setdefault('highlightthickness', 0)
        super().__init__(parent, **kwargs)
        self.size = size
        self.draw_shield()

    def draw_shield(self):
        self.delete("all")
        scale = self.size / 150.0
        
        navy_color = "#1D3557"
        white_color = "#FFFFFF"
        
        points = [
            30*scale, 20*scale,
            75*scale, 35*scale,
            120*scale, 20*scale,
            135*scale, 55*scale,
            120*scale, 100*scale,
            75*scale, 135*scale,
            30*scale, 100*scale,
            15*scale, 55*scale
        ]
        
        left_half_points = [
            30*scale, 20*scale,
            75*scale, 35*scale,
            120*scale, 20*scale,
            30*scale, 100*scale,
            15*scale, 55*scale
        ]
        
        right_half_points = [
            120*scale, 20*scale,
            135*scale, 55*scale,
            120*scale, 100*scale,
            75*scale, 135*scale,
            30*scale, 100*scale
        ]
        
        self.create_polygon(left_half_points, fill=white_color, smooth=True, tags="shield_part")
        self.create_polygon(right_half_points, fill=navy_color, smooth=True, tags="shield_part")
        self.create_polygon(points, fill="", outline=navy_color, width=int(5*scale), smooth=True, tags="shield_border")
        self.create_line(30*scale, 100*scale, 120*scale, 20*scale, fill=navy_color, width=int(2*scale))
        
        self.create_text(
            50*scale, 48*scale, 
            text="G", 
            font=("Segoe UI", int(22*scale), "bold"), 
            fill=navy_color
        )
        self.create_text(
            100*scale, 102*scale, 
            text="J", 
            font=("Segoe UI", int(22*scale), "bold"), 
            fill=white_color
        )
        self.create_text(
            77*scale, 77*scale, 
            text="P", 
            font=("Segoe UI", int(24*scale), "bold"), 
            fill=white_color
        )
        self.create_text(
            74*scale, 74*scale, 
            text="P", 
            font=("Segoe UI", int(24*scale), "bold"), 
            fill=navy_color
        )


class ClubPaymentsApp(tk.Tk):
    """
    Aplicación Principal de Gestión de Pagos, Afiliaciones y Tesorería
    Club Atlético General Paz Junior
    """
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión de Pagos - Club Atlético General Paz Junior")
        self.geometry("1120x740")
        self.minsize(1000, 650)
        
        # Paleta de Colores Institucionales GPJ
        self.colors = {
            "primary": "#1D3557",       # Azul Marino GPJ
            "secondary": "#457B9D",     # Azul Intermedio
            "accent": "#E63946",        # Rojo / Alerta Mora
            "bg_light": "#F8F9FA",      # Gris Claro de fondo
            "card_bg": "#FFFFFF",       # Blanco para tarjetas
            "text_dark": "#212529",     # Texto principal
            "text_muted": "#6C757D",    # Texto secundario
            "border": "#DEE2E6",        # Borde sutil
            "success": "#2A9D8F"        # Verde / Al día
        }
        
        self.configure(bg=self.colors["bg_light"])
        
        # Base de datos simulada de Categorías
        self.categories = {
            "1": "Sub-13",
            "2": "Sub-15",
            "3": "Sub-17",
            "4": "Primera División",
            "5": "Escuelita de Fútbol",
            "6": "Socio Recreativo"
        }
        
        # Base de datos simulada de Jugadores/Socios
        self.players = {
            "35123456": {
                "dni": "35123456",
                "nombre": "Carlos",
                "apellido": "Gaetán",
                "correo": "carlos.gaetan@generalpazjunior.com",
                "contraseña": "carlos",
                "federado": "Sí",
                "estado": "En mora",
                "categoria_id": "4",
                "meses_mora": "Julio, Agosto, Septiembre (3 meses)",
                "deuda_total": 16500.0,
                "activo": True
            },
            "22334455": {
                "dni": "22334455",
                "nombre": "Lucas",
                "apellido": "Gómez",
                "correo": "lucas.gomez@email.com",
                "contraseña": "lucas123",
                "federado": "No",
                "estado": "En mora",
                "categoria_id": "2",
                "meses_mora": "Agosto, Septiembre (2 meses)",
                "deuda_total": 11000.0,
                "activo": True
            },
            "33445566": {
                "dni": "33445566",
                "nombre": "Carlos",
                "apellido": "Rodríguez",
                "correo": "carlos.rod@email.com",
                "contraseña": "carlos123",
                "federado": "Sí",
                "estado": "En mora",
                "categoria_id": "3",
                "meses_mora": "Septiembre (1 mes)",
                "deuda_total": 5500.0,
                "activo": True
            },
            "11223344": {
                "dni": "11223344",
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@email.com",
                "contraseña": "juan123",
                "federado": "Sí",
                "estado": "Al día",
                "categoria_id": "4",
                "meses_mora": "Ninguno",
                "deuda_total": 0.0,
                "activo": True
            },
            "44556677": {
                "dni": "44556677",
                "nombre": "Andrea",
                "apellido": "Fernández",
                "correo": "andrea.f@email.com",
                "contraseña": "andrea123",
                "federado": "No",
                "estado": "Al día",
                "categoria_id": "6",
                "meses_mora": "Ninguno",
                "deuda_total": 0.0,
                "activo": True
            }
        }
        
        # Base de datos simulada de Administradores
        self.admins = {
            "admin@generalpazjunior.com": {
                "nombre": "Tesorero Principal",
                "contraseña": "admin",
                "rol": "admin"
            }
        }
        
        # Base de datos simulada de Pagos
        self.payments = [
            {
                "id_pago": "PAG001",
                "dni": "11223344",
                "tipo": "Cuota Deportiva",
                "mes": "Septiembre",
                "año": "2026",
                "monto": 5500.0,
                "comprobante": "comprobante_sep_juan.png",
                "fecha": "2026-09-15 10:30"
            },
            {
                "id_pago": "PAG002",
                "dni": "44556677",
                "tipo": "Cuota Deportiva",
                "mes": "Septiembre",
                "año": "2026",
                "monto": 5500.0,
                "comprobante": "recibo_andrea_sep.png",
                "fecha": "2026-09-16 18:45"
            },
            {
                "id_pago": "PAG003",
                "dni": "33445566",
                "tipo": "Cuota Federación",
                "mes": "Agosto",
                "año": "2026",
                "monto": 3500.0,
                "comprobante": "pago_fed_carlos.jpg",
                "fecha": "2026-08-08 09:10"
            },
            {
                "id_pago": "PAG004",
                "dni": "11223344",
                "tipo": "Cuota Deportiva",
                "mes": "Agosto",
                "año": "2026",
                "monto": 5500.0,
                "comprobante": "comprobante_ago_juan.pdf",
                "fecha": "2026-08-10 11:20"
            }
        ]
        
        self.current_user = None
        self.current_user_role = None
        
        self.setup_styles()
        
        self.container = tk.Frame(self, bg=self.colors["bg_light"])
        self.container.pack(fill="both", expand=True)
        
        self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        font_family = "Segoe UI"
        p = self.colors["primary"]
        s = self.colors["secondary"]
        bg = self.colors["bg_light"]
        card = self.colors["card_bg"]
        text = self.colors["text_dark"]
        
        self.style.configure(".", background=bg, foreground=text, font=(font_family, 10))
        self.style.configure("TEntry", fieldbackground=card, bordercolor=self.colors["border"], lightcolor=self.colors["border"], darkcolor=self.colors["border"])
        self.style.layout("TEntry", [('Entry.plain.background', {'children': [('Entry.background', {'children': [('Entry.padding', {'children': [('Entry.textarea', {'sticky': 'nswe'})], 'sticky': 'nswe'})], 'sticky': 'nswe'})], 'sticky': 'nswe'})])
        
        self.style.configure("Primary.TButton", background=p, foreground="white", font=(font_family, 10, "bold"), borderwidth=0, focuscolor=p)
        self.style.map("Primary.TButton", background=[("active", s), ("pressed", p)])
        
        self.style.configure("Secondary.TButton", background=s, foreground="white", font=(font_family, 9, "bold"), borderwidth=0)
        self.style.map("Secondary.TButton", background=[("active", p)])

        self.style.configure("Danger.TButton", background=self.colors["accent"], foreground="white", font=(font_family, 9, "bold"), borderwidth=0)
        self.style.map("Danger.TButton", background=[("active", "#BD2130")])

        self.style.configure("Success.TButton", background=self.colors["success"], foreground="white", font=(font_family, 9, "bold"), borderwidth=0)
        self.style.map("Success.TButton", background=[("active", "#1E7E34")])

        self.style.configure("Demo.TButton", background="#E9ECEF", foreground=p, font=(font_family, 8, "bold"), borderwidth=1, bordercolor=p)
        self.style.map("Demo.TButton", background=[("active", "#DEE2E6")])

        self.style.configure("Header.TLabel", font=(font_family, 16, "bold"), foreground=p, background=bg)
        self.style.configure("SubHeader.TLabel", font=(font_family, 12, "bold"), foreground=s, background=bg)
        self.style.configure("Muted.TLabel", font=(font_family, 9), foreground=self.colors["text_muted"], background=bg)
        
        self.style.configure("TNotebook", background=bg, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=card, foreground=s, padding=[12, 5], font=(font_family, 9, "bold"), borderwidth=1, bordercolor=self.colors["border"])
        self.style.map("TNotebook.Tab", background=[("selected", p)], foreground=[("selected", "white")])

        self.style.configure("Treeview", background=card, foreground=text, fieldbackground=card, rowheight=28, gridlinesvisible=True, font=(font_family, 9))
        self.style.configure("Treeview.Heading", background=self.colors["border"], foreground=p, font=(font_family, 9, "bold"))
        self.style.map("Treeview", background=[("selected", s)], foreground=[("selected", "white")])

    def load_club_logo_widget(self, parent_frame, target_size=120, bg_color="#FFFFFF"):
        """Método auxiliar para cargar y mostrar el logo del club completo y sin recortes."""
        gif_paths = ["logo_club.gif", "logo_club.gif.gif", "knowledge/logo_club.gif.gif"]
        logo_loaded = False
        img_obj = None

        for path in gif_paths:
            if os.path.exists(path):
                try:
                    full_img = tk.PhotoImage(file=path)
                    w = full_img.width()
                    h = full_img.height()
                    
                    factor_w = max(1, w // target_size)
                    factor_h = max(1, h // target_size)
                    factor = max(factor_w, factor_h)
                    
                    if factor > 1:
                        img_obj = full_img.subsample(factor)
                    else:
                        img_obj = full_img
                        
                    lbl_logo = tk.Label(parent_frame, image=img_obj, bg=bg_color)
                    lbl_logo.image = img_obj
                    lbl_logo.pack(anchor="center")
                    logo_loaded = True
                    break
                except Exception:
                    pass

        if not logo_loaded:
            shield = ClubLogoCanvas(parent_frame, size=target_size, bg=bg_color)
            shield.pack(anchor="center")

    def show_login_screen(self):
        self.clear_container()
        self.current_user = None
        self.current_user_role = None
        
        login_frame = tk.Frame(self.container, bg=self.colors["bg_light"])
        login_frame.pack(expand=True, fill="both")
        
        card = tk.Frame(login_frame, bg=self.colors["card_bg"], padx=35, pady=20, highlightbackground=self.colors["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=480)
        
        logo_container = tk.Frame(card, bg=self.colors["card_bg"])
        logo_container.pack(pady=(0, 5))
        
        self.load_club_logo_widget(logo_container, target_size=105, bg_color=self.colors["card_bg"])
            
        lbl_club = tk.Label(card, text="GENERAL PAZ JUNIOR", font=("Segoe UI", 15, "bold"), fg=self.colors["primary"], bg=self.colors["card_bg"])
        lbl_club.pack(pady=(0, 2))
        
        lbl_subtitle = tk.Label(card, text="Sistema de Gestión de Pagos e Inscripciones", font=("Segoe UI", 9), fg=self.colors["text_muted"], bg=self.colors["card_bg"])
        lbl_subtitle.pack(pady=(0, 10))

        demo_frame = tk.LabelFrame(card, text=" Acceso Rápido de Prueba ", font=("Segoe UI", 8, "bold"), fg=self.colors["secondary"], bg=self.colors["card_bg"], padx=8, pady=6)
        demo_frame.pack(fill="x", pady=(0, 12))

        def set_credentials(email, password):
            ent_email.delete(0, tk.END)
            ent_email.insert(0, email)
            ent_pass.delete(0, tk.END)
            ent_pass.insert(0, password)

        btn_demo_admin = ttk.Button(demo_frame, text="🔑 Ingresar como Admin", style="Demo.TButton", command=lambda: set_credentials("admin@generalpazjunior.com", "admin"))
        btn_demo_admin.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_demo_user = ttk.Button(demo_frame, text="👤 Ingresar como Socio (Carlos)", style="Demo.TButton", command=lambda: set_credentials("carlos.gaetan@generalpazjunior.com", "carlos"))
        btn_demo_user.pack(side="right", expand=True, fill="x", padx=(4, 0))
        
        lbl_email = tk.Label(card, text="Correo Electrónico", font=("Segoe UI", 9, "bold"), fg=self.colors["primary"], bg=self.colors["card_bg"])
        lbl_email.pack(anchor="w", pady=(2, 1))
        
        ent_email = ttk.Entry(card, width=40)
        ent_email.pack(fill="x", ipady=4, pady=(0, 8))
        
        lbl_pass = tk.Label(card, text="Contraseña", font=("Segoe UI", 9, "bold"), fg=self.colors["primary"], bg=self.colors["card_bg"])
        lbl_pass.pack(anchor="w", pady=(2, 1))
        
        ent_pass = ttk.Entry(card, show="•", width=40)
        ent_pass.pack(fill="x", ipady=4, pady=(0, 12))
        
        btn_login = ttk.Button(card, text="Iniciar Sesión", style="Primary.TButton", command=lambda: self.attempt_login(ent_email.get(), ent_pass.get()))
        btn_login.pack(fill="x", ipady=6, pady=(0, 10))
        
        links_frame = tk.Frame(card, bg=self.colors["card_bg"])
        links_frame.pack(fill="x", pady=(0, 5))
        
        lbl_forgot = tk.Label(links_frame, text="¿Olvidaste tu contraseña?", font=("Segoe UI", 9, "underline"), fg=self.colors["secondary"], bg=self.colors["card_bg"], cursor="hand2")
        lbl_forgot.pack(side="left")
        lbl_forgot.bind("<Button-1>", lambda e: self.show_forgot_password_window())
        
        lbl_register = tk.Label(links_frame, text="Registrarte", font=("Segoe UI", 9, "bold", "underline"), fg=self.colors["primary"], bg=self.colors["card_bg"], cursor="hand2")
        lbl_register.pack(side="right")
        lbl_register.bind("<Button-1>", lambda e: self.show_registration_window())

    def attempt_login(self, email, password):
        email = email.strip().lower()
        password = password.strip()
        
        if not email or not password:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos de acceso.")
            return
            
        if email in self.admins:
            if self.admins[email]["contraseña"] == password:
                self.current_user = self.admins[email]
                self.current_user_role = "admin"
                self.show_admin_dashboard()
                return
            else:
                messagebox.showerror("Acceso Denegado", "La contraseña de administrador es incorrecta.")
                return
                
        found_player = None
        for dni, p_data in self.players.items():
            if p_data["correo"].lower() == email:
                found_player = p_data
                break
                
        if found_player:
            if not found_player.get("activo", True):
                messagebox.showerror("Cuenta Inactiva", "Acceso Denegado: Su cuenta de General Paz Junior aún no ha sido activada.", parent=self)
                return
            if found_player["contraseña"] == password:
                self.current_user = found_player
                self.current_user_role = "jugador"
                self.show_player_dashboard()
                return
            else:
                messagebox.showerror("Acceso Denegado", "La contraseña ingresada es incorrecta para este socio.")
                return
                
        messagebox.showerror("Usuario no registrado", "El correo ingresado no corresponde a ningún perfil en General Paz Junior.")

    def show_forgot_password_window(self):
        top = tk.Toplevel(self)
        top.title("Recuperar Contraseña - General Paz Junior")
        top.geometry("420x260")
        top.resizable(False, False)
        top.configure(bg=self.colors["bg_light"])
        top.transient(self)
        top.grab_set()
        
        top.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - top.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")
        
        pad = tk.Frame(top, bg=self.colors["bg_light"], padx=25, pady=20)
        pad.pack(fill="both", expand=True)
        
        lbl_title = tk.Label(pad, text="¿Olvidaste tu contraseña?", font=("Segoe UI", 12, "bold"), fg=self.colors["primary"], bg=self.colors["bg_light"])
        lbl_title.pack(anchor="w", pady=(0, 10))
        
        lbl_info = tk.Label(pad, text="Ingresa tu correo electrónico registrado. Te enviaremos un correo con las instrucciones de restablecimiento de contraseña.", font=("Segoe UI", 9), fg=self.colors["text_dark"], bg=self.colors["bg_light"], justify="left", wraplength=360)
        lbl_info.pack(anchor="w", pady=(0, 15))
        
        ent_email_rec = ttk.Entry(pad, width=40)
        ent_email_rec.pack(fill="x", ipady=5, pady=(0, 15))
        ent_email_rec.focus()
        
        def procesar_recuperacion():
            email = ent_email_rec.get().strip().lower()
            if not email:
                messagebox.showwarning("Campo vacío", "Por favor ingrese su correo electrónico.", parent=top)
                return
            
            existe = email in self.admins or any(p["correo"].lower() == email for p in self.players.values())
            
            if existe:
                messagebox.showinfo("Correo de Recuperación Enviado", f"Se ha enviado un correo electrónico de recuperación a: {email}.", parent=top)
                top.destroy()
                self.show_virtual_inbox(email, "recuperacion")
            else:
                messagebox.showerror("No Encontrado", "El correo electrónico ingresado no se encuentra registrado.", parent=top)
        
        btn_submit = ttk.Button(pad, text="Enviar Mail de Recuperación", style="Primary.TButton", command=procesar_recuperacion)
        btn_submit.pack(fill="x", ipady=6)

    def show_registration_window(self):
        top = tk.Toplevel(self)
        top.title("Registro de Nuevo Socio - General Paz Junior")
        top.geometry("620x480")
        top.resizable(False, False)
        top.configure(bg=self.colors["bg_light"])
        top.transient(self)
        top.grab_set()
        
        top.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - top.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")
        
        pad = tk.Frame(top, bg=self.colors["bg_light"], padx=25, pady=20)
        pad.pack(fill="both", expand=True)
        
        lbl_title = tk.Label(pad, text="Formulario de Pre-Inscripción", font=("Segoe UI", 13, "bold"), fg=self.colors["primary"], bg=self.colors["bg_light"])
        lbl_title.pack(anchor="w", pady=(0, 10))
        
        grid_frame = tk.Frame(pad, bg=self.colors["bg_light"])
        grid_frame.pack(fill="x", pady=(0, 15))
        
        grid_frame.columnconfigure(0, weight=1, uniform="reg_col")
        grid_frame.columnconfigure(1, weight=1, uniform="reg_col")
        
        fields_layout = [
            ("DNI / Documento:", "dni", 0, 0, ""),
            ("Correo Electrónico:", "correo", 0, 1, ""),
            ("Nombre:", "nombre", 2, 0, ""),
            ("Apellido:", "apellido", 2, 1, ""),
            ("Contraseña para el portal:", "contrasenia", 4, 0, "•"),
            ("Confirmar Contraseña:", "confirmar", 4, 1, "•")
        ]
        
        entries = {}
        for label_text, key, r, c, show_char in fields_layout:
            lbl = tk.Label(grid_frame, text=label_text, font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
            lbl.grid(row=r, column=c, sticky="w", padx=10, pady=(4, 1))
            
            ent = ttk.Entry(grid_frame, show=show_char)
            ent.grid(row=r+1, column=c, sticky="ew", padx=10, pady=(0, 8))
            entries[key] = ent
            
        lbl_fed = tk.Label(grid_frame, text="¿Jugador Federado?:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
        lbl_fed.grid(row=6, column=0, sticky="w", padx=10, pady=(4, 1))
        cb_fed = ttk.Combobox(grid_frame, values=["Sí", "No"], state="readonly")
        cb_fed.set("No")
        cb_fed.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 12))
        
        lbl_cat = tk.Label(grid_frame, text="Categoría Deportiva:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
        lbl_cat.grid(row=6, column=1, sticky="w", padx=10, pady=(4, 1))
        
        cat_choices = [self.categories[k] for k in sorted(self.categories.keys(), key=int)]
        cb_cat = ttk.Combobox(grid_frame, values=cat_choices, state="readonly")
        cb_cat.set("Primera División")
        cb_cat.grid(row=7, column=1, sticky="ew", padx=10, pady=(0, 12))
        
        def procesar_register():
            dni = entries["dni"].get().strip()
            nombre = entries["nombre"].get().strip()
            apellido = entries["apellido"].get().strip()
            correo = entries["correo"].get().strip()
            contra = entries["contrasenia"].get().strip()
            confirmar = entries["confirmar"].get().strip()
            federado = cb_fed.get()
            categoria_val = cb_cat.get()
            
            if not all([dni, nombre, apellido, correo, contra, confirmar]):
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los datos del formulario.", parent=top)
                return
                
            if contra != confirmar:
                messagebox.showerror("Error de contraseña", "Las contraseñas ingresadas no coinciden.", parent=top)
                return
                
            if dni in self.players:
                messagebox.showerror("DNI Registrado", "El DNI ingresado ya se encuentra registrado como socio.", parent=top)
                return
                
            if any(p["correo"].lower() == correo.lower() for p in self.players.values()) or correo.lower() == "admin@generalpazjunior.com":
                messagebox.showerror("Correo en uso", "El correo electrónico ingresado ya está siendo utilizado por otra cuenta.", parent=top)
                return
                
            cat_id = "4"
            for k, v in self.categories.items():
                if v == categoria_val:
                    cat_id = k
                    break
            
            datos_nuevo_socio = {
                "dni": dni,
                "nombre": nombre,
                "apellido": apellido,
                "correo": correo,
                "contraseña": contra,
                "federado": federado,
                "estado": "En mora",
                "categoria_id": cat_id,
                "activo": False
            }
            self.players[dni] = datos_nuevo_socio
            
            messagebox.showinfo("Confirmación Requerida", f"Pre-inscripción iniciada para: {correo}.", parent=top)
            top.destroy()
            self.show_virtual_inbox(correo, "registro", datos_nuevo_socio)
            
        btn_register = ttk.Button(pad, text="Confirmar Registro", style="Primary.TButton", command=procesar_register)
        btn_register.pack(fill="x", ipady=8, pady=(10, 0))

    def show_virtual_inbox(self, email, mode, datos_nuevo_socio=None):
        top_inbox = tk.Toplevel(self)
        top_inbox.title("Servidor de Correo GPJ - General Paz Junior")
        top_inbox.geometry("600x480")
        top_inbox.resizable(False, False)
        top_inbox.configure(bg="#F1F3F4")
        top_inbox.transient(self)
        top_inbox.grab_set()
        
        top_inbox.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - top_inbox.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - top_inbox.winfo_height()) // 2
        top_inbox.geometry(f"+{x}+{y}")
        
        header = tk.Frame(top_inbox, bg="#1D3557", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="GPJ Mail - Servidor de Correo de Simulación", font=("Segoe UI", 11, "bold"), fg="white", bg="#1D3557").pack(side="left", padx=15)
        tk.Label(header, text=f"Bandeja de: {email}", font=("Segoe UI", 9, "italic"), fg="#A8DADC", bg="#1D3557").pack(side="right", padx=15)
        
        body = tk.Frame(top_inbox, bg="white", padx=20, pady=20)
        body.pack(fill="both", expand=True, padx=15, pady=15)
        
        if mode == "registro":
            tk.Label(body, text="Asunto: ¡Bienvenido a General Paz Junior! Confirma tu cuenta", font=("Segoe UI", 11, "bold"), fg="#212529", bg="white").pack(anchor="w", pady=(0, 5))
            tk.Label(body, text="De: admin@generalpazjunior.com  |  Para: " + email, font=("Segoe UI", 8), fg="#6C757D", bg="white").pack(anchor="w", pady=(0, 15))
            tk.Frame(body, bg="#DEE2E6", height=1).pack(fill="x", pady=(0, 15))
            
            msg_text = "Gracias por iniciar tu proceso de inscripción en el Club Atlético General Paz Junior.\n\nHaz clic en el botón para confirmar tu cuenta:"
            tk.Label(body, text=msg_text, font=("Segoe UI", 9.5), fg="#212529", bg="white", justify="left", wraplength=520).pack(anchor="w", pady=(0, 20))
            
            def confirmar_cuenta():
                dni = datos_nuevo_socio["dni"]
                self.players[dni] = datos_nuevo_socio
                self.players[dni]["activo"] = True
                messagebox.showinfo("Cuenta Activada", "Tu cuenta ha sido activada con éxito.", parent=top_inbox)
                top_inbox.destroy()
                
            btn_confirmar = ttk.Button(body, text="[ CONFIRMAR REGISTRO DE CUENTA ]", style="Success.TButton", command=confirmar_cuenta)
            btn_confirmar.pack(pady=15, ipady=8, fill="x")
            
        elif mode == "recuperacion":
            tk.Label(body, text="Asunto: Recuperación de Contraseña - General Paz Junior", font=("Segoe UI", 11, "bold"), fg="#212529", bg="white").pack(anchor="w", pady=(0, 5))
            tk.Label(body, text="De: soporte@generalpazjunior.com  |  Para: " + email, font=("Segoe UI", 8), fg="#6C757D", bg="white").pack(anchor="w", pady=(0, 15))
            tk.Frame(body, bg="#DEE2E6", height=1).pack(fill="x", pady=(0, 15))
            
            form_restablecer = tk.Frame(body, bg="white")
            def mostrar_form_restablecer():
                btn_rec.pack_forget()
                form_restablecer.pack(fill="x", pady=10)
                
            btn_rec = ttk.Button(body, text="[ RESTABLECER CONTRASEÑA ]", style="Primary.TButton", command=mostrar_form_restablecer)
            btn_rec.pack(pady=10, ipady=8, fill="x")
            
            lbl_new_pass = tk.Label(form_restablecer, text="Nueva Contraseña:", font=("Segoe UI", 9, "bold"), fg="#1D3557", bg="white")
            lbl_new_pass.pack(anchor="w", pady=(5, 2))
            ent_new_pass = ttk.Entry(form_restablecer, show="•", width=40)
            ent_new_pass.pack(fill="x", ipady=4, pady=(0, 8))
            
            lbl_new_pass_conf = tk.Label(form_restablecer, text="Confirmar Nueva Contraseña:", font=("Segoe UI", 9, "bold"), fg="#1D3557", bg="white")
            lbl_new_pass_conf.pack(anchor="w", pady=(5, 2))
            ent_new_pass_conf = ttk.Entry(form_restablecer, show="•", width=40)
            ent_new_pass_conf.pack(fill="x", ipady=4, pady=(0, 15))
            
            def guardar_nueva_clave():
                nueva = ent_new_pass.get().strip()
                conf = ent_new_pass_conf.get().strip()
                if not nueva or not conf or nueva != conf:
                    messagebox.showerror("Error", "Verifique las contraseñas ingresadas.", parent=top_inbox)
                    return
                if email in self.admins:
                    self.admins[email]["contraseña"] = nueva
                else:
                    for p in self.players.values():
                        if p["correo"].lower() == email:
                            p["contraseña"] = nueva
                            break
                messagebox.showinfo("Contraseña Restablecida", "¡Tu contraseña ha sido actualizada!", parent=top_inbox)
                top_inbox.destroy()
                
            btn_guardar_rec = ttk.Button(form_restablecer, text="Guardar Nueva Contraseña", style="Success.TButton", command=guardar_nueva_clave)
            btn_guardar_rec.pack(fill="x", ipady=5)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ========================================================
    # SECCIÓN: RECUADRO REUTILIZABLE PARA AÑADIR PAGO
    # ========================================================
    def create_add_payment_box(self, parent_frame, target_dni, on_success_callback=None):
        """
        Crea el recuadro 'Recuadro de Registro / Añadir Pago' exactamente según la interfaz
        solicitada, con desplegables para Tipo de Pago, Mes, Año, un campo de MONTO LIBRE DE ESCRITURA (Entry),
        y el botón para adjuntar imagen de comprobante desde el dispositivo.
        """
        box = tk.LabelFrame(
            parent_frame,
            text=" 💳 Recuadro de Registro / Añadir Pago ",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["card_bg"],
            padx=15,
            pady=12,
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        box.pack(fill="x", expand=False, pady=(0, 12))

        # Fila 0: Tipo de Pago y Mes
        lbl_tipo = tk.Label(box, text="Tipo de Pago:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_tipo.grid(row=0, column=0, sticky="w", padx=5, pady=4)

        cb_tipo = ttk.Combobox(box, values=["Cuota Deportiva", "Cuota Federación", "Inscripción Anual"], state="readonly", width=18)
        cb_tipo.set("Cuota Federación")
        cb_tipo.grid(row=0, column=1, sticky="w", padx=5, pady=4)

        lbl_mes = tk.Label(box, text="Mes:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_mes.grid(row=0, column=2, sticky="w", padx=(15, 5), pady=4)

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        cb_mes = ttk.Combobox(box, values=meses, state="readonly", width=15)
        cb_mes.set("Septiembre")
        cb_mes.grid(row=0, column=3, sticky="w", padx=5, pady=4)

        # Fila 1: Año y Monto (ESCRITURA LIBRE MANUAL)
        lbl_ano = tk.Label(box, text="Año:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_ano.grid(row=1, column=0, sticky="w", padx=5, pady=4)

        anos = ["2024", "2025", "2026", "2027", "2028"]
        cb_ano = ttk.Combobox(box, values=anos, state="readonly", width=18)
        cb_ano.set("2026")
        cb_ano.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        lbl_monto = tk.Label(box, text="Monto ($):", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_monto.grid(row=1, column=2, sticky="w", padx=(15, 5), pady=4)

        # Campo de Entrada de Texto LIBRE para el monto ($)
        ent_monto = ttk.Entry(box, width=17)
        ent_monto.insert(0, "3500.00")
        ent_monto.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        def update_monto_sugerido(event):
            tipo_val = cb_tipo.get()
            ent_monto.delete(0, tk.END)
            if tipo_val == "Cuota Deportiva":
                ent_monto.insert(0, "5500.00")
            elif tipo_val == "Cuota Federación":
                ent_monto.insert(0, "3500.00")
            elif tipo_val == "Inscripción Anual":
                ent_monto.insert(0, "10000.00")

        cb_tipo.bind("<<ComboboxSelected>>", update_monto_sugerido)

        # Fila 2: Adjuntar Comprobante (Imagen)
        lbl_comp = tk.Label(box, text="Comprobante (Imagen):", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_comp.grid(row=2, column=0, sticky="w", padx=5, pady=4)

        file_subframe = tk.Frame(box, bg=self.colors["card_bg"])
        file_subframe.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=4)

        ent_file_path = ttk.Entry(file_subframe, width=32)
        ent_file_path.insert(0, "Ninguna imagen seleccionada")
        ent_file_path.configure(state="readonly")
        ent_file_path.pack(side="left", padx=(0, 8), fill="x", expand=True)

        def seleccionar_imagen():
            archivo_path = filedialog.askopenfilename(
                title="Seleccionar Imagen de Comprobante",
                filetypes=[
                    ("Imágenes y PDF", "*.png *.jpg *.jpeg *.gif *.webp *.bmp *.pdf"),
                    ("Todos los archivos", "*.*")
                ]
            )
            if archivo_path:
                nombre_archivo = os.path.basename(archivo_path)
                ent_file_path.configure(state="normal")
                ent_file_path.delete(0, tk.END)
                ent_file_path.insert(0, nombre_archivo)
                ent_file_path.configure(state="readonly")

        btn_browse = ttk.Button(file_subframe, text="📁 Buscar Imagen...", style="Secondary.TButton", command=seleccionar_imagen)
        btn_browse.pack(side="right")

        # Fila 3: Botón de Confirmación "Añadir Pago"
        def ejecutar_add_pago():
            tipo_p = cb_tipo.get()
            mes_p = cb_mes.get()
            ano_p = cb_ano.get()
            monto_val = ent_monto.get().strip()
            comp_file = ent_file_path.get()

            if not monto_val:
                messagebox.showerror("Error de Validación", "Debe ingresar un monto para el pago.")
                return

            try:
                monto_float = float(monto_val.replace("$", "").replace(",", ""))
            except ValueError:
                messagebox.showerror("Error de Formato", "El monto ingresado debe ser un número numérico válido (ej: 3500.00).")
                return

            if comp_file in ["", "Ninguna imagen seleccionada"]:
                messagebox.showwarning("Comprobante Requerido", "Por favor, adjunte una imagen del comprobante de transferencia desde su dispositivo.")
                return

            t_dni_str = str(target_dni).strip()
            new_id = f"PAG{len(self.payments)+1:03d}"
            nuevo_pago = {
                "id_pago": new_id,
                "dni": t_dni_str,
                "tipo": f"{tipo_p}",
                "mes": f"{mes_p}",
                "año": f"{ano_p}",
                "monto": monto_float,
                "comprobante": comp_file,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            self.payments.append(nuevo_pago)

            # Impacto directo e inmediato en la base de datos de socios
            p_name = f"Socio #{t_dni_str}"
            cat_desc = "Categoría General"
            c_mail = "socio@generalpazjunior.com"
            for k, p in self.players.items():
                if str(k).strip() == t_dni_str or str(p.get("dni", "")).strip() == t_dni_str:
                    p["estado"] = "Al día"
                    p["meses_mora"] = "Ninguno"
                    p["meses_deuda"] = "Ninguno"
                    p["deuda_total"] = 0.0
                    p["monto_deuda"] = 0.0
                    p_name = f"{p['nombre']} {p['apellido']}"
                    cat_desc = self.categories.get(p.get("categoria_id"), "Categoría General")
                    c_mail = p.get("correo", c_mail)

            # Si el usuario actual es el jugador que paga, actualizar su estado en memoria activa
            if self.current_user and str(self.current_user.get("dni", "")).strip() == t_dni_str:
                self.current_user["estado"] = "Al día"
                self.current_user["meses_mora"] = "Ninguno"
                self.current_user["deuda_total"] = 0.0

            # Registrar Alerta/Notificación completa para la campanita de Tesorería
            notif = {
                "id": new_id,
                "socio": p_name,
                "dni": t_dni_str,
                "correo": c_mail,
                "categoria": cat_desc,
                "monto": monto_float,
                "concepto": f"{tipo_p} ({mes_p} {ano_p})",
                "tipo": tipo_p,
                "mes": mes_p,
                "ano": ano_p,
                "año": ano_p,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "comprobante": comp_file,
                "leido": False
            }
            if not hasattr(self, 'notifications'):
                self.notifications = []
            self.notifications.append(notif)

            msg_info = (
                f"Abono acreditado para el socio DNI #{t_dni_str}:\n\n"
                f"• ID Pago: {new_id}\n"
                f"• Período: {mes_p} {ano_p}\n"
                f"• Monto: ${monto_float:,.2f}\n"
                f"• Archivo: {comp_file}\n\n"
                f"El estado del socio ha sido actualizado a: AL DÍA."
            )
            messagebox.showinfo("¡Pago Registrado Exitosamente!", msg_info)

            if on_success_callback:
                try:
                    on_success_callback()
                except Exception:
                    pass

        btn_add = ttk.Button(box, text="➕ Añadir y Registrar Pago", style="Success.TButton", command=ejecutar_add_pago)
        btn_add.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=(8, 4), ipady=4)

        return box

    # ========================================================
    # SECCIÓN: DASHBOARD DEL JUGADOR / SOCIO
    # ========================================================
    def show_player_dashboard(self):
        self.clear_container()
        
        nav_bar = tk.Frame(self.container, bg=self.colors["primary"], height=60)
        nav_bar.pack(fill="x", side="top")
        nav_bar.pack_propagate(False)
        
        logo_mini_container = tk.Frame(nav_bar, bg=self.colors["primary"])
        logo_mini_container.pack(side="left", padx=15)
        self.load_club_logo_widget(logo_mini_container, target_size=40, bg_color=self.colors["primary"])
            
        lbl_welcome = tk.Label(nav_bar, text=f"Portal de Socios - Hola, {self.current_user['nombre']} {self.current_user['apellido']}", font=("Segoe UI", 12, "bold"), fg="white", bg=self.colors["primary"])
        lbl_welcome.pack(side="left", padx=10)
        
        btn_logout = ttk.Button(nav_bar, text="Cerrar Sesión", style="Secondary.TButton", command=self.show_login_screen)
        btn_logout.pack(side="right", padx=15, pady=10)
        
        main_body = tk.Frame(self.container, bg=self.colors["bg_light"], padx=20, pady=20)
        main_body.pack(fill="both", expand=True)
        
        card_estado = tk.Frame(main_body, bg=self.colors["card_bg"], highlightbackground=self.colors["border"], highlightthickness=1, padx=20, pady=15)
        card_estado.pack(fill="x", pady=(0, 15))
        
        lbl_estado_titulo = tk.Label(card_estado, text="DATOS REGISTRADOS DEL ATLETA", font=("Segoe UI", 11, "bold"), fg=self.colors["secondary"], bg=self.colors["card_bg"])
        lbl_estado_titulo.pack(anchor="w", pady=(0, 10))
        
        info_and_logo_frame = tk.Frame(card_estado, bg=self.colors["card_bg"])
        info_and_logo_frame.pack(fill="x", expand=True)
        
        details_grid = tk.Frame(info_and_logo_frame, bg=self.colors["card_bg"])
        details_grid.pack(side="left", fill="both", expand=True)
        
        labels_info = [
            ("Nombre Completo:", f"{self.current_user['nombre']} {self.current_user['apellido']}"),
            ("DNI del Jugador:", self.current_user["dni"]),
            ("Correo Electrónico:", self.current_user["correo"]),
            ("Categoría Deportiva:", self.categories.get(self.current_user["categoria_id"], "Sin Categoría")),
            ("Jugador Federado:", self.current_user["federado"]),
        ]
        
        for i, (label_txt, value_txt) in enumerate(labels_info):
            row_idx = i % 3
            col_idx = (i // 3) * 2
            
            lbl_title = tk.Label(details_grid, text=label_txt, font=("Segoe UI", 9, "bold"), fg=self.colors["text_muted"], bg=self.colors["card_bg"])
            lbl_title.grid(row=row_idx, column=col_idx, sticky="w", padx=(10, 5), pady=4)
            
            lbl_value = tk.Label(details_grid, text=value_txt, font=("Segoe UI", 10), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
            lbl_value.grid(row=row_idx, column=col_idx+1, sticky="w", padx=(0, 30), pady=4)
            
        lbl_est_title = tk.Label(details_grid, text="Condición de Pago:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_muted"], bg=self.colors["card_bg"])
        lbl_est_title.grid(row=2, column=2, sticky="w", padx=(10, 5), pady=4)
        
        estado = self.current_user["estado"]
        badge_color = self.colors["success"] if estado == "Al día" else self.colors["accent"]
        lbl_badge = tk.Label(details_grid, text=f"  {estado.upper()}  ", font=("Segoe UI", 10, "bold"), fg="white", bg=badge_color, padx=5, pady=2)
        lbl_badge.grid(row=2, column=3, sticky="w", pady=4)

        # Logo COMPLETO
        logo_right_container = tk.Frame(info_and_logo_frame, bg=self.colors["card_bg"], padx=15)
        logo_right_container.pack(side="right", anchor="e")
        self.load_club_logo_widget(logo_right_container, target_size=100, bg_color=self.colors["card_bg"])
        
        # Pestañas inferiores para jugador
        notebook = ttk.Notebook(main_body, style="TNotebook")
        notebook.pack(fill="both", expand=True)
        
        tab_historial = tk.Frame(notebook, bg=self.colors["bg_light"], pady=10)
        notebook.add(tab_historial, text="Mis Pagos Registrados")
        self.draw_player_payments_table(tab_historial)
        
        tab_registrar = tk.Frame(notebook, bg=self.colors["bg_light"], pady=10)
        notebook.add(tab_registrar, text="Subir Comprobante de Pago")
        self.create_add_payment_box(tab_registrar, target_dni=self.current_user["dni"], on_success_callback=self.show_player_dashboard)

    def draw_player_payments_table(self, parent, target_dni=None):
        """Muestra los pagos de un socio con filtro por mes y año, visor de comprobantes y diseño idéntico al administrador."""
        for widget in parent.winfo_children():
            widget.destroy()

        lbl_titulo_p = tk.Label(
            parent, 
            text="HISTORIAL DE PAGOS REGISTRADOS DE MI CUENTA (Doble Clic para Ver Comprobante)", 
            font=("Segoe UI", 11, "bold"), 
            fg=self.colors["primary"], 
            bg=self.colors["bg_light"]
        )
        lbl_titulo_p.pack(side="top", anchor="w", pady=(0, 5))

        # 1. Barra de Filtro por Mes y Año
        filter_card = tk.LabelFrame(
            parent, 
            text=" 🔍 Filtro por Mes y Año ", 
            font=("Segoe UI", 9, "bold"), 
            fg=self.colors["secondary"], 
            bg=self.colors["card_bg"], 
            padx=12, 
            pady=8
        )
        filter_card.pack(side="top", fill="x", pady=(0, 10))

        lbl_f_mes = tk.Label(filter_card, text="Filtrar Mes:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_f_mes.grid(row=0, column=0, sticky="w", padx=5)

        meses_list = ["Todos los Meses", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        cb_f_mes = ttk.Combobox(filter_card, values=meses_list, state="readonly", width=18)
        cb_f_mes.set("Todos los Meses")
        cb_f_mes.grid(row=0, column=1, sticky="w", padx=5)

        lbl_f_ano = tk.Label(filter_card, text="Filtrar Año:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_f_ano.grid(row=0, column=2, sticky="w", padx=(15, 5))

        anos_list = ["Todos los Años", "2024", "2025", "2026", "2027", "2028"]
        cb_f_ano = ttk.Combobox(filter_card, values=anos_list, state="readonly", width=15)
        cb_f_ano.set("Todos los Años")
        cb_f_ano.grid(row=0, column=3, sticky="w", padx=5)

        # (Botón de cobro removido de Socios Activos)

        # Contenedor para Treeview y Scrollbar
        tree_container = tk.Frame(frame_izq, bg=self.colors["bg_light"])
        tree_container.pack(side="top", fill="both", expand=True)
        
        columns = ("dni", "nombre", "correo", "categoria", "federado", "estado")
        tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("dni", text="DNI")
        tree.heading("nombre", text="Nombre y Apellido")
        tree.heading("correo", text="Correo Electrónico")
        tree.heading("categoria", text="Categoría")
        tree.heading("federado", text="Federado")
        tree.heading("estado", text="Estado de Cuenta")
        
        tree.column("dni", width=95, anchor="center")
        tree.column("nombre", width=170, anchor="w")
        tree.column("correo", width=190, anchor="w")
        tree.column("categoria", width=120, anchor="center")
        tree.column("federado", width=80, anchor="center")
        tree.column("estado", width=100, anchor="center")
        
        for dni, p in self.players.items():
            if not p.get("activo", True):
                continue
            cat_name = self.categories.get(p["categoria_id"], "Sin Categoría")
            tree.insert("", "end", values=(
                p["dni"],
                f"{p['nombre']} {p['apellido']}",
                p["correo"],
                cat_name,
                p["federado"],
                p["estado"]
            ))
            
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        # Panel derecho para inscripción de nuevos socios
        frame_der = tk.LabelFrame(
            parent, 
            text=" Nueva Ficha de Socio ", 
            font=("Segoe UI", 10, "bold"), 
            fg=self.colors["primary"], 
            bg=self.colors["bg_light"], 
            padx=15, 
            pady=10
        )
        frame_der.pack(side="right", fill="both", width=340)
        
        fields = [
            ("DNI del Jugador:", "dni"),
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Correo Electrónico:", "correo")
        ]
        
        entries = {}
        for i, (lbl_text, key) in enumerate(fields):
            lbl = tk.Label(frame_der, text=lbl_text, font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
            lbl.pack(anchor="w", pady=(5, 1))
            ent = ttk.Entry(frame_der)
            ent.pack(fill="x", ipady=3, pady=(0, 8))
            entries[key] = ent
            
        lbl_cat = tk.Label(frame_der, text="Categoría de Inscripción:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
        lbl_cat.pack(anchor="w", pady=(5, 1))
        
        cb_cat_reg = ttk.Combobox(frame_der, values=list(self.categories.values()), state="readonly")
        cb_cat_reg.set("Sub-15")
        cb_cat_reg.pack(fill="x", pady=(0, 8))
        
        lbl_fed = tk.Label(frame_der, text="¿Está Federado?:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["bg_light"])
        lbl_fed.pack(anchor="w", pady=(5, 1))
        
        var_fed = tk.StringVar(value="No")
        chk_fed_y = ttk.Radiobutton(frame_der, text="Sí", variable=var_fed, value="Sí")
        chk_fed_y.pack(side="left", padx=10, pady=(0, 10))
        chk_fed_n = ttk.Radiobutton(frame_der, text="No", variable=var_fed, value="No")
        chk_fed_n.pack(side="left", padx=10, pady=(0, 10))
        
        tk.Frame(frame_der, bg=self.colors["bg_light"], height=10).pack(fill="both")
        
        def save_new_player():
            dni = entries["dni"].get().strip()
            nombre = entries["nombre"].get().strip()
            apellido = entries["apellido"].get().strip()
            correo = entries["correo"].get().strip()
            categoria_sel = cb_cat_reg.get()
            federado = var_fed.get()
            
            if not dni or not nombre or not apellido or not correo:
                messagebox.showerror("Campos incompletos", "Por favor, complete todos los campos requeridos para la afiliación.")
                return
                
            if dni in self.players:
                messagebox.showerror("Error de Registro", "El DNI ingresado ya se encuentra registrado en el sistema.")
                return
                
            cat_id = "1"
            for k, v in self.categories.items():
                if v == categoria_sel:
                    cat_id = k
                    break
                    
            password_def = nombre.lower()
            
            self.players[dni] = {
                "dni": dni,
                "nombre": nombre,
                "apellido": apellido,
                "correo": correo,
                "contraseña": password_def,
                "federado": federado,
                "estado": "En mora",
                "categoria_id": cat_id,
                "activo": True,
                "meses_deuda": "Recién registrado (1 mes)",
                "deuda_total": 5500.0
            }
            
            messagebox.showinfo("Socio Registrado", f"Socio '{nombre} {apellido}' incorporado exitosamente.\nContraseña por defecto: '{password_def}'")
            self.switch_admin_view("Socios activos")
            
        btn_save = ttk.Button(frame_der, text="Registrar Afiliado", style="Primary.TButton", command=save_new_player)
        btn_save.pack(fill="x", ipady=5, side="bottom", pady=(10, 0))

    # --------------------------------------------------------
    # VISTA 2: SOCIOS EN MORA (DEUDORES)
    # --------------------------------------------------------
    def render_admin_socios_en_mora(self, parent):
        """Muestra el listado completo de todos los socios en mora con detalles de deuda"""
        lbl_titulo_d = tk.Label(
            parent, 
            text="INFORMES DE DEUDA Y MOROSIDAD - LISTADO COMPLETO DE SOCIOS EN MORA", 
            font=("Segoe UI", 11, "bold"), 
            fg=self.colors["accent"], 
            bg=self.colors["bg_light"]
        )
        lbl_titulo_d.pack(side="top", anchor="w", pady=(0, 10))

        action_frame = tk.Frame(parent, bg=self.colors["bg_light"], pady=10)
        action_frame.pack(side="bottom", fill="x")

        def get_sel_debtor_dni():
            selected = tree_debtors.selection()
            if selected:
                item_vals = tree_debtors.item(selected[0], "values")
                return str(item_vals[0]).strip()
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un socio en mora de la lista.")
            return None

        def open_selected_debtor_payment():
            dni = get_sel_debtor_dni()
            if dni:
                self.open_admin_player_payment_window(dni)

        def notify_all_debtors():
            debtors_count = sum(1 for p in self.players.values() if p.get("activo", True) and p["estado"] == "En mora")
            if debtors_count == 0:
                messagebox.showinfo("Control de Deuda", "Excelente. No hay socios en mora actualmente.")
                return
            messagebox.showinfo("Avisos Enviados", f"Se han enviado {debtors_count} avisos de cobro y recordatorios automáticos de pago vía email a los socios deudores.")

        lbl_summary = tk.Label(action_frame, text="", font=("Segoe UI", 10, "bold"), fg=self.colors["accent"], bg=self.colors["bg_light"])
        lbl_summary.pack(side="left")

        btn_reg_pago_d = ttk.Button(
            action_frame, 
            text="💳 Registrar Pago a Deudor", 
            style="Success.TButton", 
            command=open_selected_debtor_payment
        )
        btn_reg_pago_d.pack(side="right", padx=(10, 0))

        btn_notify = ttk.Button(
            action_frame, 
            text="Enviar Recordatorios de Pago Masivos", 
            style="Danger.TButton", 
            command=notify_all_debtors
        )
        btn_notify.pack(side="right", padx=(0, 10))

        tree_container = tk.Frame(parent, bg=self.colors["bg_light"])
        tree_container.pack(side="top", fill="both", expand=True)

        columns = ("dni", "nombre", "categoria", "meses_deuda", "deuda_total", "estado")
        tree_debtors = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        tree_debtors.heading("dni", text="DNI")
        tree_debtors.heading("nombre", text="Nombre y Apellido")
        tree_debtors.heading("categoria", text="Categoría")
        tree_debtors.heading("meses_deuda", text="Meses Adeudados")
        tree_debtors.heading("deuda_total", text="Deuda Total ($)")
        tree_debtors.heading("estado", text="Estado")

        tree_debtors.column("dni", width=100, anchor="center")
        tree_debtors.column("nombre", width=180, anchor="w")
        tree_debtors.column("categoria", width=130, anchor="center")
        tree_debtors.column("meses_deuda", width=220, anchor="w")
        tree_debtors.column("deuda_total", width=120, anchor="e")
        tree_debtors.column("estado", width=100, anchor="center")

        debtors_count = 0
        monto_total_deuda = 0.0
        for dni, p in self.players.items():
            if not p.get("activo", True):
                continue
            if p["estado"] == "En mora":
                cat_name = self.categories.get(p["categoria_id"], "Sin Categoría")
                m_deuda = p.get("meses_mora", p.get("meses_deuda", "1 mes"))
                val_deuda = float(p.get("deuda_total", p.get("monto_deuda", 5500.0)))
                tree_debtors.insert("", "end", values=(
                    p["dni"],
                    f"{p['nombre']} {p['apellido']}",
                    cat_name,
                    m_deuda,
                    f"${val_deuda:,.2f}",
                    p["estado"]
                ))
                debtors_count += 1
                monto_total_deuda += val_deuda

        lbl_summary.config(text=f"Total de Jugadores en Mora: {debtors_count}   |   Deuda Acumulada: ${monto_total_deuda:,.2f}")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree_debtors.yview)
        tree_debtors.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        tree_debtors.pack(side="left", fill="both", expand=True)

        tree_debtors.bind("<Double-1>", lambda e: open_selected_debtor_payment())

    # --------------------------------------------------------
    # VISTA 3: HISTORIAL DE PAGO (CON FILTRO POR MES Y AÑO)
    # --------------------------------------------------------
    def render_admin_historial_pagos(self, parent):
        """Muestra el listado completo de todos los pagos con un filtro por mes y año"""
        lbl_titulo_p = tk.Label(
            parent, 
            text="HISTORIAL UNIFICADO DE PAGOS RECIBIDOS (Doble Clic para Ver Comprobante)", 
            font=("Segoe UI", 11, "bold"), 
            fg=self.colors["primary"], 
            bg=self.colors["bg_light"]
        )
        lbl_titulo_p.pack(side="top", anchor="w", pady=(0, 5))

        # 1. Barra de Filtro por Mes y Año
        filter_card = tk.LabelFrame(
            parent, 
            text=" 🔍 Filtro por Mes y Año ", 
            font=("Segoe UI", 9, "bold"), 
            fg=self.colors["secondary"], 
            bg=self.colors["card_bg"], 
            padx=12, 
            pady=8
        )
        filter_card.pack(side="top", fill="x", pady=(0, 10))

        lbl_f_mes = tk.Label(filter_card, text="Filtrar Mes:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_f_mes.grid(row=0, column=0, sticky="w", padx=5)

        meses_list = ["Todos los Meses", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        cb_f_mes = ttk.Combobox(filter_card, values=meses_list, state="readonly", width=18)
        cb_f_mes.set("Todos los Meses")
        cb_f_mes.grid(row=0, column=1, sticky="w", padx=5)

        lbl_f_ano = tk.Label(filter_card, text="Filtrar Año:", font=("Segoe UI", 9, "bold"), fg=self.colors["text_dark"], bg=self.colors["card_bg"])
        lbl_f_ano.grid(row=0, column=2, sticky="w", padx=(15, 5))

        anos_list = ["Todos los Años", "2024", "2025", "2026", "2027", "2028"]
        cb_f_ano = ttk.Combobox(filter_card, values=anos_list, state="readonly", width=15)
        cb_f_ano.set("Todos los Años")
        cb_f_ano.grid(row=0, column=3, sticky="w", padx=5)

        # Botón de acción al pie
        action_p_frame = tk.Frame(parent, bg=self.colors["bg_light"], pady=8)
        action_p_frame.pack(side="bottom", fill="x")

        def ver_comprobante_pago():
            selected = tree_all_payments.selection()
            if not selected:
                messagebox.showwarning("Auditoría de Pagos", "Por favor, seleccione un pago de la tabla para abrir el comprobante.")
                return
            item_values = tree_all_payments.item(selected[0], "values")
            p_id = item_values[0]
            match = next((p for p in self.payments if p["id_pago"] == p_id), None)
            if match:
                self.show_payment_receipt_dialog(match)
            else:
                match = {
                    "id_pago": item_values[0],
                    "socio": item_values[1],
                    "tipo": item_values[2],
                    "mes": item_values[3],
                    "año": item_values[4],
                    "monto": float(item_values[5].replace("$", "").replace(",", "").strip()),
                    "comprobante": item_values[6],
                    "fecha": item_values[7]
                }
                self.show_payment_receipt_dialog(match)

        btn_audit = ttk.Button(
            action_p_frame, 
            text="👁️ Ver y Validar Comprobante Seleccionado", 
            style="Primary.TButton", 
            command=ver_comprobante_pago
        )
        btn_audit.pack(side="right")

        tree_container = tk.Frame(parent, bg=self.colors["bg_light"])
        tree_container.pack(side="top", fill="both", expand=True)

        columns = ("id_pago", "socio", "tipo", "mes", "año", "monto", "comprobante", "fecha")
        tree_all_payments = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        tree_all_payments.heading("id_pago", text="ID Pago")
        tree_all_payments.heading("socio", text="Asociado / Identificación")
        tree_all_payments.heading("tipo", text="Tipo de Pago")
        tree_all_payments.heading("mes", text="Mes")
        tree_all_payments.heading("año", text="Año")
        tree_all_payments.heading("monto", text="Monto ($)")
        tree_all_payments.heading("comprobante", text="Archivo Adjunto")
        tree_all_payments.heading("fecha", text="Fecha de Cobro")

        tree_all_payments.column("id_pago", width=80, anchor="center")
        tree_all_payments.column("socio", width=220, anchor="w")
        tree_all_payments.column("tipo", width=140, anchor="w")
        tree_all_payments.column("mes", width=85, anchor="center")
        tree_all_payments.column("año", width=75, anchor="center")
        tree_all_payments.column("monto", width=95, anchor="e")
        tree_all_payments.column("comprobante", width=200, anchor="w")
        tree_all_payments.column("fecha", width=140, anchor="center")

        def aplicar_filtro_tabla(event=None):
            # Limpiar tabla
            for item in tree_all_payments.get_children():
                tree_all_payments.delete(item)

            mes_sel = cb_f_mes.get()
            ano_sel = cb_f_ano.get()

            for p in reversed(self.payments):
                # Aplicar lógica de filtro
                if mes_sel != "Todos los Meses" and p.get("mes") != mes_sel:
                    continue
                if ano_sel != "Todos los Años" and str(p.get("año", "")) != ano_sel:
                    continue

                p_name = "Desconocido"
                if p["dni"] in self.players:
                    player_obj = self.players[p["dni"]]
                    p_name = f"{player_obj['nombre']} {player_obj['apellido']} (DNI #{p['dni']})"
                elif "socio" in p:
                    p_name = p["socio"]
                    
                tree_all_payments.insert("", "end", values=(
                    p["id_pago"],
                    p_name,
                    p["tipo"],
                    p["mes"],
                    p.get("año", "2026"),
                    f"${p['monto']:,.2f}",
                    p["comprobante"],
                    p["fecha"]
                ))

        btn_filter = ttk.Button(filter_card, text="🔍 Aplicar Filtro", style="Primary.TButton", command=aplicar_filtro_tabla)
        btn_filter.grid(row=0, column=4, padx=(15, 5))

        def limpiar_filtro_tabla():
            cb_f_mes.set("Todos los Meses")
            cb_f_ano.set("Todos los Años")
            aplicar_filtro_tabla()

        btn_reset = ttk.Button(filter_card, text="🔄 Limpiar Filtros", style="Secondary.TButton", command=limpiar_filtro_tabla)
        btn_reset.grid(row=0, column=5, padx=5)

        cb_f_mes.bind("<<ComboboxSelected>>", aplicar_filtro_tabla)
        cb_f_ano.bind("<<ComboboxSelected>>", aplicar_filtro_tabla)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree_all_payments.yview)
        tree_all_payments.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        tree_all_payments.pack(side="left", fill="both", expand=True)

        tree_all_payments.bind("<Double-1>", lambda e: ver_comprobante_pago())
        
        # Carga inicial sin filtros
        aplicar_filtro_tabla()

    def open_admin_player_payment_window(self, player_dni, on_success_callback=None):
        """
        Abre la Ventana Emergente Exclusiva para Registrar Pago con Desplegables de Mes, Año, Monto Libre y Adjuntar Comprobante.
        Al completar la carga, actualiza automáticamente las tablas de la administración y cambia a la vista de Historial de Pago.
        """
        if player_dni not in self.players:
            messagebox.showerror("Error", "No se encontró el socio seleccionado.")
            return

        player = self.players[player_dni]
        
        top_pay = tk.Toplevel(self)
        top_pay.title(f"Registrar Pago - Socio: {player['nombre']} {player['apellido']} (DNI #{player_dni})")
        top_pay.geometry("640x480")
        top_pay.configure(bg=self.colors["bg_light"])
        top_pay.transient(self)
        top_pay.grab_set()

        top_pay.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - top_pay.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - top_pay.winfo_height()) // 2
        top_pay.geometry(f"+{x}+{y}")

        pad = tk.Frame(top_pay, bg=self.colors["bg_light"], padx=20, pady=15)
        pad.pack(fill="both", expand=True)

        card_info = tk.Frame(pad, bg=self.colors["card_bg"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=10)
        card_info.pack(fill="x", pady=(0, 12))

        header_split = tk.Frame(card_info, bg=self.colors["card_bg"])
        header_split.pack(fill="x", expand=True)

        left_data = tk.Frame(header_split, bg=self.colors["card_bg"])
        left_data.pack(side="left", fill="both", expand=True)

        lbl_head = tk.Label(left_data, text=f"COBRANZA DIGITAL DE SOCIO #{player['dni']}", font=("Segoe UI", 11, "bold"), fg=self.colors["primary"], bg=self.colors["card_bg"])
        lbl_head.pack(anchor="w", pady=(0, 4))

        cat_str = self.categories.get(player["categoria_id"], "Sin Categoría")
        details_str = f"• Socio: {player['nombre']} {player['apellido']}\n• Correo: {player['correo']}\n• Categoría: {cat_str} | Estado Actual: {player['estado'].upper()}"
        
        lbl_sub = tk.Label(
            left_data,
            text=details_str,
            font=("Segoe UI", 9),
            fg=self.colors["text_dark"],
            bg=self.colors["card_bg"],
            justify="left"
        )
        lbl_sub.pack(anchor="w")

        logo_right = tk.Frame(header_split, bg=self.colors["card_bg"], padx=5)
        logo_right.pack(side="right", anchor="e")
        self.load_club_logo_widget(logo_right, target_size=65, bg_color=self.colors["card_bg"])

        def on_done():
            top_pay.destroy()
            if on_success_callback:
                on_success_callback()
            self.show_admin_dashboard()
            if hasattr(self, 'admin_view_var'):
                self.admin_view_var.set("Historial de pago")
                self.switch_admin_view("Historial de pago")

        self.create_add_payment_box(pad, target_dni=player_dni, on_success_callback=on_done)


if __name__ == '__main__':
    try:
        app = ClubPaymentsApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print('==================================================')
        print('ERROR AL INICIAR LA APLICACIÓN DE GENERAL PAZ JUNIOR:')
        print('==================================================')
        traceback.print_exc()
        print('==================================================')
        input('Presiona ENTER para cerrar esta ventana...')
