import subprocess
import re

class WiFiEngine:
    """
    Motor encargado de interactuar con el sistema nativo de Windows (netsh)
    para auditar redes y recuperar perfiles.
    """
    
    @staticmethod
    def get_available_networks():
        """Escanea y parsea redes Wi-Fi visibles a una lista de diccionarios."""
        try:
            output = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], 
                                           encoding='cp850', errors='ignore')
            
            networks = []
            current_net = {}
            
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith("SSID"):
                    if current_net: networks.append(current_net)
                    ssid = re.search(r":\s(.*)", line)
                    current_net = {"ssid": ssid.group(1).strip() if ssid else "Oculta", "bssids": []}
                elif "Autenticaci" in line:
                    auth = re.search(r":\s(.*)", line)
                    current_net["auth"] = auth.group(1).strip() if auth else "Desconocida"
                elif "BSSID" in line:
                    bssid = re.search(r":\s(.*)", line)
                    if bssid: current_net["bssids"].append({"mac": bssid.group(1).strip()})
                elif "Señal" in line or "Signal" in line:
                    signal = re.search(r":\s(\d+)%", line)
                    if signal and current_net["bssids"]:
                        current_net["bssids"][-1]["signal"] = signal.group(1)
                elif "Canal" in line or "Channel" in line:
                    channel = re.search(r":\s(\d+)", line)
                    if channel and current_net["bssids"]:
                        current_net["bssids"][-1]["channel"] = channel.group(1)

            if current_net: networks.append(current_net)
            return networks
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def get_manufacturer(mac):
        """Identificación de fabricante basada en prefijos OUI comunes."""
        prefixes = {
            "00:0A:F7": "TP-Link", "00:14:6C": "Netgear", "A4:2B:B0": "Huawei",
            "C8:3A:35": "Tenda", "00:E0:4C": "Realtek", "B8:27:EB": "Raspberry Pi",
            "00:1D:AA": "D-Link", "00:25:9C": "Cisco-Linksys", "2C:30:33": "Asus",
            "E8:94:F6": "TP-Link", "60:E3:27": "TP-Link", "14:CC:20": "TP-Link",
            "00:17:C5": "Intel", "04:BF:6D": "ZTE", "70:3E:AC": "Apple"
        }
        prefix = mac.upper()[:8]
        return prefixes.get(prefix, "Desconocido")

    @staticmethod
    def test_connection(ssid, password):
        """
        Intenta realizar una conexión de prueba para validar la robustez de la clave.
        Útil para auditorías empresariales de contraseñas por defecto.
        """
        xml_profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        profile_path = f"C:/Users/Usuario/Desktop/redeswifi/temp_profile.xml"
        try:
            with open(profile_path, "w") as f:
                f.write(xml_profile)
            
            # Importar perfil temporal
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"], capture_all=True)
            
            # Intentar conectar
            cmd = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_all=True)
            
            # Esperar un momento y verificar estado
            import time
            time.sleep(2)
            status_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding='cp850', errors='ignore')
            
            # Limpiar
            subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"], capture_all=True)
            
            if f"SSID                  : {ssid}" in status_output and "Conectado" in status_output:
                return True
            return False
        except Exception as e:
            return False

    @staticmethod
    def get_saved_profiles():
        """Obtiene la lista de nombres de perfiles Wi-Fi guardados en el equipo."""
        try:
            output = subprocess.check_output(["netsh", "wlan", "show", "profiles"], 
                                           encoding='cp850', errors='ignore')
            profiles = re.findall(r":\s(.*)", output)
            return [p.strip() for p in profiles if p.strip()]
        except Exception as e:
            return []

    @staticmethod
    def get_password(profile_name):
        """
        Recupera la contraseña de un perfil específico.
        Requiere que el perfil exista en el sistema.
        """
        try:
            output = subprocess.check_output(["netsh", "wlan", "show", "profile", 
                                            profile_name, "key=clear"], 
                                           encoding='cp850', errors='ignore')
            password_match = re.search(r"(?:Contenido de la clave|Key Content)\s*:\s*(.*)", output)
            if password_match:
                return password_match.group(1).strip()
            return "No encontrada (posiblemente red abierta)"
        except Exception:
            return "Error al recuperar (requiere Admin)"

class Auditor:
    """Motor de reglas para auditoría defensiva."""
    
    @staticmethod
    def audit_profile(profile_name, password):
        issues = []
        if len(password) < 8:
            issues.append("Contraseña demasiado corta (vulnerable a fuerza bruta).")
        if password == profile_name:
            issues.append("Contraseña idéntica al SSID (extremadamente inseguro).")
        
        return issues if issues else ["Configuración básica aceptable."]
