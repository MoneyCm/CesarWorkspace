import customtkinter as ctk
import threading
import time
from datetime import datetime
from wifi_manager import WifiManager
import logging

# Setup customtkinter appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class WifiMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Monitor SEC_GOBIERNO")
        self.geometry("500x450")
        self.resizable(False, False)

        self.wifi_manager = WifiManager()
        self.monitoring = False
        self.check_interval_seconds = 300  # Default 5 minutes
        self.timer_id = None

        # GUI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.header_frame, 
            text="Estado: Desconocido", 
            font=("Roboto", 18, "bold"),
            text_color="gray"
        )
        self.status_label.pack(pady=10)

        # Controls
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.control_frame, text="Frecuencia (min):").pack(side="left", padx=10)
        
        self.interval_var = ctk.StringVar(value="5")
        self.interval_menu = ctk.CTkOptionMenu(
            self.control_frame, 
            values=["1", "5", "10", "15", "30", "60"],
            variable=self.interval_var,
            command=self.update_interval_settings
        )
        self.interval_menu.pack(side="left", padx=10)

        self.monitor_switch = ctk.CTkSwitch(
            self.control_frame, 
            text="Monitoreo Activo", 
            command=self.toggle_monitoring
        )
        self.monitor_switch.select() # Start active
        self.monitor_switch.pack(side="right", padx=10)

        # Connect Button
        self.recon_button = ctk.CTkButton(
            self.control_frame,
            text="Reconectar Ahora",
            width=120,
            command=self.manual_reconnect_trigger
        )
        self.recon_button.pack(side="right", padx=10)

        # Logs
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.log_box.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")

        # Footer
        self.last_check_label = ctk.CTkLabel(self, text="Última verificación: Nunca", text_color="gray")
        self.last_check_label.grid(row=3, column=0, pady=(0, 10))

        # Admin Warning Label
        self.admin_label = ctk.CTkLabel(self, text="", text_color="orange", font=("Roboto", 11))
        self.admin_label.grid(row=4, column=0, pady=(0, 10))
        self.check_admin_status()

        # Start automatic monitoring loop
        self.monitoring = True
        self.run_verification_loop()

    def check_admin_status(self):
        if not self.wifi_manager.is_admin():
            self.admin_label.configure(
                text="⚠️ Sin permisos de Administrador: El auto-encendido podría fallar."
            )
        else:
            self.admin_label.configure(text="✅ Ejecutando como Administrador.", text_color="green")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", full_msg)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_interval_settings(self, choice):
        self.check_interval_seconds = int(choice) * 60
        self.log(f"Frecuencia actualizada a {choice} minutos.")
        # Restart timer if running to apply new interval immediately (optional, or just wait for next)
        # For simplicity, we just let the next loop pick it up, or we could cancel and restart.

    def toggle_monitoring(self):
        if self.monitor_switch.get() == 1:
            self.monitoring = True
            self.log("Monitoreo REANUDADO.")
            self.run_verification_loop()
        else:
            self.monitoring = False
            self.log("Monitoreo PAUSADO.")
            if self.timer_id:
                self.after_cancel(self.timer_id)
                self.timer_id = None

    def run_verification_loop(self):
        if not self.monitoring:
            return

        self.perform_check()
        
        # Schedule next check
        # Convert selected minutes to ms
        ms_interval = int(self.interval_var.get()) * 60 * 1000
        self.timer_id = self.after(ms_interval, self.run_verification_loop)

    def perform_check(self):
        # Update UI to show checking (optional, but good feedback)
        self.last_check_label.configure(text=f"Verificando... ({datetime.now().strftime('%H:%M:%S')})")
        
        # Run check logic (non-blocking if possible, but netsh is fast enough for main thread usually. 
        # For strict UI responsiveness, threading is better, but this is simple.)
        
        current_ssid = self.wifi_manager.get_current_ssid()
        target = "SEC_GOBIERNO"
        
        if current_ssid is False:
            self.status_label.configure(text="WI-FI APAGADO", text_color="orange")
            self.log("CRITICAL: El Wi-Fi está apagado.")
            self.log("Intentando encender Wi-Fi automáticamente...")
            success, msg = self.wifi_manager.enable_wifi()
            self.log(f"RESULT: {msg}")
            if success:
                # If we successfully sent the command, try to reconnect in 5 seconds
                self.log("Esperando 5s para que la antena inicie...")
                self.after(5000, self.perform_check)
            else:
                self.log("TIP: Haz clic derecho y 'Ejecutar como administrador'.")
        elif current_ssid == target:
            is_connected = True
            self.status_label.configure(text=f"Conectado a {target}", text_color="green")
            self.log("OK: Conectado.")
        else:
            self.status_label.configure(text="DESCONECTADO", text_color="red")
            self.log(f"ALERT: No conectado a {target}. Actual: {current_ssid if current_ssid else 'Nada'}")
            self.attempt_reconnect()

        self.last_check_label.configure(text=f"Última verificación: {datetime.now().strftime('%H:%M:%S')}")

    def attempt_reconnect(self):
        self.log("Intentando reconectar...")
        success, message = self.wifi_manager.connect_to_target()
        if success:
            self.log(f"INFO: {message}")
            self.log("Verificando estado en 10s...")
            # Schedule a quick follow-up check
            self.after(10000, self.perform_check) 
        else:
            self.log(f"ERROR: {message}")
            if "apagada" in message.lower() or "turned off" in message.lower() or "disponible" in message.lower():
                self.log("INFO: Detectado Wi-Fi apagado. Intentando encender automáticamente...")
                success_enable, enable_msg = self.wifi_manager.enable_wifi()
                self.log(f"RESULT: {enable_msg}")
                if success_enable:
                    self.log("Esperando 5s para reintentar conexión...")
                    self.after(5000, self.perform_check)
                else:
                    self.log("TIP: Haz clic derecho y 'Ejecutar como administrador'.")
            elif "not found" in message.lower():
                self.log("TIP: Asegúrate de que la red esté en rango.")

    def manual_reconnect_trigger(self):
        self.log("MANUAL: Forzando verificación y reconexión...")
        self.perform_check()

if __name__ == "__main__":
    app = WifiMonitorApp()
    app.mainloop()
