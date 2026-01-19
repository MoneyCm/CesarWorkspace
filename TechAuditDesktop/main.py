import os
import sys
import psutil
import cpuinfo
import GPUtil
import platform
import webbrowser
import datetime
import subprocess
import customtkinter as ctk
from PIL import Image

class TechAuditApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Base Path Logic ---
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.reports_dir = os.path.join(self.base_dir, "Reportes_Auditoria")
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

        # --- Window Config ---
        self.title("TechAudit Desktop")
        self.geometry("700x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # --- UI Elements ---
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=80)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="TechAudit Desktop", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=20)

        self.scan_button = ctk.CTkButton(
            self.header_frame, 
            text="INICIAR DIAGNÓSTICO", 
            command=self.run_audit,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.scan_button.pack(side="right", padx=20, pady=20)

        # Content Area (Scrollable)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.cards = {}

    def get_storage_info(self):
        storage_data = []
        try:
            # Simple check for SSD vs HDD on Windows
            # Media Type 4 = SSD, 3 = HDD
            cmd = 'wmic diskdrive get model,size,mediatype /format:list'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8')
            
            drives = output.split('\r\r\n\r\r\n')
            for drive in drives:
                if not drive.strip(): continue
                info = {}
                for line in drive.split('\r\r\n'):
                    if '=' in line:
                        k, v = line.split('=', 1)
                        info[k.strip()] = v.strip()
                if info:
                    storage_data.append(info)
        except:
            pass
        return storage_data

    def run_audit(self):
        # Reset UI
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.scan_button.configure(state="disabled", text="ESCANEANDO...")
        self.update()

        try:
            # 1. CPU Info
            cpu_info = cpuinfo.get_cpu_info()
            cpu_model = cpu_info.get('brand_raw', "Desconocido")
            
            # 2. RAM Info
            ram = psutil.virtual_memory()
            ram_gb = round(ram.total / (1024**3), 2)
            
            # 3. GPU Info
            gpus = GPUtil.getGPUs()
            gpu_name = gpus[0].name if gpus else "Integrada / No Detectada"
            
            # 4. Storage
            storage = self.get_storage_info()
            storage_text = ""
            is_ssd = False
            for s in storage:
                m_type = s.get('MediaType', 'Unknown')
                size_gb = round(int(s.get('Size', 0)) / (1024**3), 2)
                storage_text += f"{s.get('Model', 'Drive')}: {size_gb}GB ({m_type})\n"
                if "SSD" in m_type or "Solid State" in m_type or "4" in m_type:
                    is_ssd = True

            # --- Display Cards ---
            self.add_card("CPU", cpu_model, "processor")
            self.add_card("Memoria RAM", f"{ram_gb} GB", "memory")
            self.add_card("GPU", gpu_name, "video-card")
            self.add_card("Almacenamiento", storage_text or "Detectado por sistema", "hard-drive")

            # --- Upgrade Alerts ---
            alerts = []
            if ram_gb < 8:
                alerts.append(("🔴 Urgente: Aumentar RAM (Mínimo 8GB recomendado)", "#ff4d4d"))
            if not is_ssd and storage:
                alerts.append(("🟡 Sugerencia: Migrar a SSD para mejorar velocidad", "#ffcc00"))

            if alerts:
                alert_frame = ctk.CTkFrame(self.content_frame, fg_color="#2b2b2b", border_width=1, border_color="#555")
                alert_frame.pack(fill="x", pady=10, padx=5)
                ctk.CTkLabel(alert_frame, text="RECOMENDACIONES DE SOFTWARE/HARDWARE", font=ctk.CTkFont(weight="bold")).pack(pady=5)
                for msg, color in alerts:
                    ctk.CTkLabel(alert_frame, text=msg, text_color=color).pack(anchor="w", padx=10)

            # --- Price Buttons ---
            btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=20)

            ctk.CTkButton(
                btn_frame, 
                text="Buscar CPU en Amazon", 
                command=lambda: webbrowser.open(f"https://www.amazon.com/s?k={cpu_model}"),
                fg_color="#f39c12", hover_color="#e67e22"
            ).pack(side="left", padx=5, expand=True)

            ctk.CTkButton(
                btn_frame, 
                text="Buscar RAM en MercadoLibre", 
                command=lambda: webbrowser.open(f"https://listado.mercadolibre.com.co/ram-{ram_gb}gb"),
                fg_color="#f1c40f", text_color="black", hover_color="#d4ac0d"
            ).pack(side="left", padx=5, expand=True)

            # --- Save Report ---
            self.save_report(cpu_model, ram_gb, gpu_name, storage_text, alerts)

        except Exception as e:
            ctk.CTkLabel(self.content_frame, text=f"Error en diagnóstico: {str(e)}", text_color="red").pack()
        
        finally:
            self.scan_button.configure(state="normal", text="INICIAR DIAGNÓSTICO")

    def add_card(self, title, content, icon_name):
        card = ctk.CTkFrame(self.content_frame, height=100)
        card.pack(fill="x", pady=5, padx=5)
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#3498db")
        title_lbl.pack(anchor="w", padx=15, pady=(10, 0))
        
        content_lbl = ctk.CTkLabel(card, text=content, font=ctk.CTkFont(size=14), wraplength=600, justify="left")
        content_lbl.pack(anchor="w", padx=15, pady=(0, 10))

    def save_report(self, cpu, ram, gpu, storage, alerts):
        hostname = platform.node()
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Reporte_{hostname}_{date_str}.txt"
        file_path = os.path.join(self.reports_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"--- REPORTE DE AUDITORÍA TECHAUDIT ---\n")
            f.write(f"Equipo: {hostname}\n")
            f.write(f"Fecha: {datetime.datetime.now()}\n")
            f.write(f"OS: {platform.system()} {platform.release()}\n")
            f.write("-" * 40 + "\n")
            f.write(f"CPU: {cpu}\n")
            f.write(f"RAM: {ram} GB\n")
            f.write(f"GPU: {gpu}\n")
            f.write(f"Almacenamiento:\n{storage}\n")
            f.write("-" * 40 + "\n")
            f.write("RECOMENDACIONES:\n")
            for msg, _ in alerts:
                f.write(f"- {msg}\n")
            if not alerts:
                f.write("- El sistema parece estar en buen estado.\n")

        print(f"Reporte guardado en: {file_path}")

if __name__ == "__main__":
    app = TechAuditApp()
    app.mainloop()
