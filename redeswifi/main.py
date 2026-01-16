import customtkinter as ctk
from wifi_engine import WiFiEngine
import webbrowser
import re

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RedesWiFi - Auditoría y Recuperación")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="REDES\nWIFI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=20)

        self.btn_scan = ctk.CTkButton(self.sidebar, text="Escanear Entorno", command=self.scan_networks)
        self.btn_scan.grid(row=1, column=0, padx=20, pady=10)

        self.btn_recovery = ctk.CTkButton(self.sidebar, text="Mis Contraseñas", command=self.recover_passwords)
        self.btn_recovery.grid(row=2, column=0, padx=20, pady=10)

        self.btn_stress = ctk.CTkButton(self.sidebar, text="Test de Robustez", 
                                       fg_color="#d35400", hover_color="#e67e22",
                                       command=self.show_stress_test)
        self.btn_stress.grid(row=3, column=0, padx=20, pady=10)

        # Main View
        self.main_view = ctk.CTkScrollableFrame(self, label_text="Panel de Auditoría")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def scan_networks(self):
        self.clear_main_view()
        networks = WiFiEngine.get_available_networks()
        
        if not networks:
            ctk.CTkLabel(self.main_view, text="No se detectaron redes o el adaptador está apagado.").pack(pady=20)
            return

        for net in networks:
            card = ctk.CTkFrame(self.main_view)
            card.pack(fill="x", padx=10, pady=5)
            
            # Info básica
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=10, pady=10, fill="y")
            
            # Icono de señal visual (barras)
            signal_val = int(net['bssids'][0].get('signal', 0)) if net['bssids'] else 0
            color = "#ff0000" if signal_val < 30 else "#ffcc00" if signal_val < 70 else "#00ff00"
            
            signal_bar = ctk.CTkProgressBar(info_frame, width=50, height=10, progress_color=color)
            signal_bar.set(signal_val / 100)
            signal_bar.pack(anchor="w", pady=(0, 5))

            ctk.CTkLabel(info_frame, text=net['ssid'], font=("Arial", 16, "bold")).pack(anchor="w")
            
            # Fabricante y Seguridad
            mac = net['bssids'][0].get('mac', '') if net['bssids'] else ''
            vendor = WiFiEngine.get_manufacturer(mac)
            
            details_text = f"Fabricante: {vendor} | Seguridad: {net.get('auth', 'N/A')}"
            ctk.CTkLabel(info_frame, text=details_text, font=("Arial", 11)).pack(anchor="w")
            
            # Detalles técnicos
            if net['bssids']:
                b = net['bssids'][0]
                tech = f"Signal: {signal_val}% | Canal: {b.get('channel', '?')} | MAC: {mac}"
                ctk.CTkLabel(info_frame, text=tech, font=("Consolas", 9), text_color="gray").pack(anchor="w")

            # Botón de Auditoría
            btn_audit = ctk.CTkButton(card, text="Auditar", width=80, 
                                     command=lambda n=net: self.run_audit(n))
            btn_audit.pack(side="right", padx=10)

    def run_audit(self, network):
        issues = []
        if network.get('auth') in ["Abierta", "Open", "WEP"]:
            issues.append(f"CRÍTICO: Cifrado {network['auth']} es inseguro.")
        
        match = re.search(r"WPA[1-2]", network.get('auth', ''))
        if not match and network.get('auth') not in ["WEP", "Abierta"]:
            issues.append("ADVERTENCIA: Se recomienda WPA3 para redes modernas.")

        # Mostrar resultados en una ventana emergente o sección
        from tkinter import messagebox
        report = "\n".join(issues) if issues else "No se detectaron vulnerabilidades críticas inmediatas."
        messagebox.showinfo(f"Auditoría: {network['ssid']}", report)

    def recover_passwords(self):
        self.clear_main_view()
        profiles = WiFiEngine.get_saved_profiles()
        
        if not profiles:
            label = ctk.CTkLabel(self.main_view, text="No se encontraron perfiles guardados.")
            label.pack(pady=20)
            return

        for profile in profiles:
            pwd = WiFiEngine.get_password(profile)
            card = ctk.CTkFrame(self.main_view)
            card.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(card, text=f"SSID: {profile}", font=("Arial", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(card, text=f"Clave: {pwd}", text_color="#00ff00").pack(side="right", padx=10)

    def show_stress_test(self):
        self.clear_main_view()
        ctk.CTkLabel(self.main_view, text="Auditoría de Fuerza Bruta (Diccionario)", 
                    font=("Arial", 18, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.main_view, text="SSID Objetivo:", anchor="w").pack(fill="x", padx=20)
        self.entry_ssid = ctk.CTkEntry(self.main_view, placeholder_text="Ej: RedInfraestructura")
        self.entry_ssid.pack(fill="x", padx=20, pady=5)

        file_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(file_frame, text="Diccionario de claves:", anchor="w").pack(side="left")
        self.btn_load_file = ctk.CTkButton(file_frame, text="Cargar Archivo .txt", 
                                          width=120, command=self.load_dictionary_file)
        self.btn_load_file.pack(side="right")

        self.txt_passwords = ctk.CTkTextbox(self.main_view, height=150)
        self.txt_passwords.pack(fill="x", padx=20, pady=5)
        self.txt_passwords.insert("0.0", "admin123\n12345678\npassword\nInvicta2024\nEmpresa2024")

        self.btn_run_stress = ctk.CTkButton(self.main_view, text="INICIAR PRUEBA DE PENETRACIÓN", 
                                           fg_color="#c0392b", command=self.run_stress_audit)
        self.btn_run_stress.pack(pady=20)

        self.progress_text = ctk.CTkLabel(self.main_view, text="")
        self.progress_text.pack()

    def load_dictionary_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.txt_passwords.delete("0.0", "end")
                self.txt_passwords.insert("0.0", content)

    def run_stress_audit(self):
        ssid = self.entry_ssid.get()
        passwords = self.txt_passwords.get("0.0", "end").split("\n")
        passwords = [p.strip() for p in passwords if p.strip()]

        if not ssid:
            from tkinter import messagebox
            messagebox.showerror("Error", "Carga un SSID válido.")
            return

        audit_results = []
        found = False
        
        for pwd in passwords:
            self.progress_text.configure(text=f"Probando: {pwd}...")
            self.update()
            
            if WiFiEngine.test_connection(ssid, pwd):
                found = True
                audit_results.append({"ssid": ssid, "auth": "WPA2 (Test)", 
                                     "status": "VULNERABLE", 
                                     "recommendations": [f"Clave '{pwd}' hallada en diccionario.", "Cambiar a clave compleja (WPA3 si es posible)."]})
                break
        
        from tkinter import messagebox
        if found:
            messagebox.showwarning("VULNERABILIDAD HALLADA", 
                                 f"¡ÉXITO! La red '{ssid}' es vulnerable.\n"
                                 "Se recomienda generar un reporte ahora.")
            self.export_audit_report(audit_results)
        else:
            messagebox.showinfo("Auditoría Finalizada", "No se encontraron claves débiles.")

    def export_audit_report(self, data):
        from reports import ReportGenerator
        filename = ReportGenerator.generate_txt_report(data)
        from tkinter import messagebox
        messagebox.showinfo("Reporte Generado", f"El informe se ha guardado como:\n{filename}")

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
