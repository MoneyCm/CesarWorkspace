import subprocess
import re
import logging
import ctypes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TARGET_SSID = "SEC_GOBIERNO"

TARGET_SSID = "SEC_GOBIERNO"

class WifiManager:
    def is_admin(self):
        """Checks if the script is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def get_current_ssid(self):
        """Returns current SSID, None if disconnected, or False if interface is OFF."""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=True,
                shell=True
            )
            output = result.stdout
            
            # Check if interface is disconnected/off
            if "Software Off" in output or "desconectado" in output.lower() or "dehabilitado" in output.lower():
                if "Software Off" in output or "estado : desconectado" in output.lower() and "conectado" not in output.lower():
                     # If the output strictly says disconnected but doesn't show an interface status, 
                     # we look for the "State" field.
                     pass

            # Check for State: disconnected or similar
            state_match = re.search(r"^\s*Estado\s*:\s*(.*)$", output, re.MULTILINE | re.IGNORECASE)
            if not state_match:
                state_match = re.search(r"^\s*State\s*:\s*(.*)$", output, re.MULTILINE | re.IGNORECASE)
            
            if state_match and "disconnected" in state_match.group(1).lower():
                return None # Interface is on but not connected
            
            # Look for "SSID"
            match = re.search(r"^\s*SSID\s*:\s*(.*)$", output, re.MULTILINE)
            if match:
                return match.group(1).strip()
            
            # If no SSID and we contextually see the interface is off:
            if "apagada" in output.lower() or "turned off" in output.lower() or "disconnected from" in output.lower():
                # On some versions, it just says "The interface is powered off"
                if "apagada" in output.lower() or "powered off" in output.lower() or "software off" in output.lower():
                    return False # Special flag for Interface OFF
                
            return None
        except Exception as e:
            logging.error(f"Error checking Wifi status: {e}")
            return None

    def is_connected_to_target(self):
        """Checks if connected to the specific target network."""
        current = self.get_current_ssid()
        logging.info(f"Current SSID: {current}")
        return current == TARGET_SSID

    def connect_to_target(self):
        """Attempts to connect to the target network using its profile."""
        try:
            logging.info(f"Attempting to connect to {TARGET_SSID}...")
            # Command to connect. Requires the profile to exist.
            cmd = ["netsh", "wlan", "connect", f"name={TARGET_SSID}"]
            # Use shell=True for better handling of command output in some Windows environments
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logging.info("Connection command sent successfully.")
                return True, "Comando enviado. Windows está procesando la conexión..."
            else:
                error_msg = result.stdout if result.stdout else result.stderr
                logging.error(f"Failed to send connect command: {error_msg}")
                
                # Specialized error message for disabled interface
                if "apagada" in error_msg.lower() or "turned off" in error_msg.lower():
                    return False, "⚠️ INTERFAZ APAGADA: Debes encender el WiFi en Windows."
                
                return False, f"Error de Windows: {error_msg.strip()}"
        except Exception as e:
            logging.error(f"Exception during connection attempt: {e}")
            return False, f"Error interno: {str(e)}"

    def enable_wifi(self):
        """Attempts to enable the WiFi radio via command line."""
        try:
            logging.info("Attempting to enable WiFi radio...")
            # This command attempts to turn on the radio
            cmd = ["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enabled"]
            subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            # Also try the specific wlan radio command
            cmd_radio = ["netsh", "wlan", "set", "radio", "state=enabled"]
            result = subprocess.run(cmd_radio, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                return True, "Se intentó encender el Wi-Fi automáticamente."
            else:
                return False, "No se pudo encender automáticamente (posiblemente requiere permisos de Administrador)."
        except Exception as e:
            logging.error(f"Exception while enabling wifi: {e}")
            return False, str(e)
