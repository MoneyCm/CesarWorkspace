import json
from datetime import datetime

class ReportGenerator:
    """Genera reportes de auditoría en formato JSON y Texto."""
    
    @staticmethod
    def generate_txt_report(audit_data):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"auditoria_{timestamp}.txt"
        
        with open(f"C:/Users/Usuario/Desktop/redeswifi/{filename}", "w", encoding="utf-8") as f:
            f.write("=== REPORTE DE AUDITORÍA DEFENSIVA REDESWIFI ===\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("="*48 + "\n\n")
            
            for net in audit_data:
                f.write(f"SSID: {net['ssid']}\n")
                f.write(f"Seguridad: {net['auth']}\n")
                f.write(f"Estado: {net['status']}\n")
                f.write("Recomendaciones:\n")
                for rec in net['recommendations']:
                    f.write(f" - {rec}\n")
                f.write("-" * 20 + "\n")
        
        return filename
