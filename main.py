import customtkinter as ctk
import threading
import os
from hardware_info import get_system_info
from upgrade_advisor import analyze_upgrades
from market_valuation import get_search_links, open_search
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class HardwareAuditApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HardwareAudit USB")
        self.geometry("900x600")

        # Layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_dashboard = self.tab_view.add("Resumen del Sistema")
        self.tab_upgrades = self.tab_view.add("Análisis de Mejoras")
        self.tab_valuation = self.tab_view.add("Valoración de Mercado")

        self.tab_dashboard.grid_columnconfigure(0, weight=1)
        self.tab_upgrades.grid_columnconfigure(0, weight=1)
        self.tab_valuation.grid_columnconfigure(0, weight=1)

        # Data Holder
        self.system_data = {}

        # Loading Label
        self.loading_label = ctk.CTkLabel(self, text="Escaneando Hardware... Por favor espere", font=("Roboto", 16))
        self.loading_label.grid(row=0, column=0)
        self.tab_view.grid_forget() # Hide tabs until loaded

        # Start Scanc
        thread = threading.Thread(target=self.load_data)
        thread.start()

    def load_data(self):
        self.system_data = get_system_info()
        self.after(100, self.setup_ui)

    def setup_ui(self):
        self.loading_label.destroy()
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.setup_dashboard()
        self.setup_upgrades()
        self.setup_valuation()

    def setup_dashboard(self):
        # Frame for info
        frame = ctk.CTkScrollableFrame(self.tab_dashboard)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        row = 0
        data_map = {
            "Sistema Operativo": self.system_data.get('os'),
            "Procesador (CPU)": self.system_data.get('cpu_model'),
            "Núcleos CPU": self.system_data.get('cpu_cores'),
            "Frecuencia CPU": self.system_data.get('cpu_freq'),
            "Memoria RAM Total": self.system_data.get('ram_total'),
            "Memoria RAM Usada": f"{self.system_data.get('ram_used')} ({self.system_data.get('ram_percent')})",
            "Tarjeta Gráfica (GPU)": self.system_data.get('gpu'),
            "Almacenamiento": self.system_data.get('storage'),
            "Tipo Disco Principal": self.system_data.get('main_disk_type')
        }

        for label, value in data_map.items():
            lbl_title = ctk.CTkLabel(frame, text=f"{label}:", font=("Roboto", 14, "bold"), anchor="w")
            lbl_title.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            lbl_val = ctk.CTkLabel(frame, text=str(value), font=("Roboto", 14), anchor="w", wraplength=400)
            lbl_val.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            row += 1

        # Export Button
        btn_export = ctk.CTkButton(self.tab_dashboard, text="Exportar Informe (.txt)", command=self.export_report)
        btn_export.grid(row=1, column=0, pady=10)

    def setup_upgrades(self):
        frame = ctk.CTkScrollableFrame(self.tab_upgrades)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)

        suggestions = analyze_upgrades(self.system_data)

        for i, item in enumerate(suggestions):
            # Card-like frame for each suggestion
            card = ctk.CTkFrame(frame)
            card.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            
            color = "white"
            if item['status'] == "Crítico" or item['status'] == "Antiguo":
                color = "#ff5555" # Red-ish
            elif item['status'] == "Mejorable":
                color = "#ffb86c" # Orange-ish
            else:
                color = "#50fa7b" # Green-ish

            title = ctk.CTkLabel(card, text=f"{item['component']} - {item['status']}", text_color=color, font=("Roboto", 16, "bold"))
            title.pack(anchor="w", padx=10, pady=(10,0))
            
            desc = ctk.CTkLabel(card, text=item['advice'], wraplength=600, justify="left")
            desc.pack(anchor="w", padx=10, pady=(5,10))

    def setup_valuation(self):
        frame = ctk.CTkScrollableFrame(self.tab_valuation)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        components_to_value = [
            ("Procesador", self.system_data.get('cpu_model')),
            ("Tarjeta Gráfica", self.system_data.get('gpu')),
            ("Memoria RAM", f"{self.system_data.get('ram_total')} RAM") # Generic search
        ]

        row = 0
        for name, model in components_to_value:
            if not model or model == "Desconocido": continue
            
            lbl = ctk.CTkLabel(frame, text=f"{name}: {model}", font=("Roboto", 14, "bold"))
            lbl.grid(row=row, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="w")
            row += 1

            links = get_search_links(model)
            
            # Buttons
            btn_ml = ctk.CTkButton(frame, text="Buscar en MercadoLibre CO", 
                                 fg_color="#ffe600", text_color="black", hover_color="#f5db00",
                                 command=lambda u=links['MercadoLibre CO']: open_search(u))
            btn_ml.grid(row=row, column=0, padx=5, pady=5)
            
            btn_ebay = ctk.CTkButton(frame, text="Buscar en eBay", 
                                   fg_color="#0064d2", hover_color="#0054b2",
                                   command=lambda u=links['eBay']: open_search(u))
            btn_ebay.grid(row=row, column=1, padx=5, pady=5)
            row += 1

        # Manual Estimation
        lbl_est = ctk.CTkLabel(frame, text="--- Estimación Manual (Experimental) ---", font=("Roboto", 14))
        lbl_est.grid(row=row, column=0, columnspan=2, pady=(30, 10))
        row += 1
        
        lbl_info = ctk.CTkLabel(frame, text="* Los precios varían mucho.", text_color="gray")
        lbl_info.grid(row=row, column=0, columnspan=2)

    def export_report(self):
        filename = "system_report.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== REPORTE HARDWARE AUDIT ===\n")
            f.write(f"Generado: {datetime.now()}\n\n")
            for k, v in self.system_data.items():
                f.write(f"{k}: {v}\n")
            
            f.write("\n=== SUGERENCIAS DE MEJORA ===\n")
            sug = analyze_upgrades(self.system_data)
            for item in sug:
                f.write(f"- [{item['status']}] {item['component']}: {item['advice']}\n")
                
        # Simple popup
        top = ctk.CTkToplevel(self)
        top.title("Exportado")
        top.geometry("300x100")
        l = ctk.CTkLabel(top, text=f"Informe guardado como {filename}")
        l.pack(expand=True)

if __name__ == "__main__":
    # Fix for Windows infinite spawn loop with PyInstaller
    import multiprocessing
    multiprocessing.freeze_support()
    
    app = HardwareAuditApp()
    app.mainloop()
