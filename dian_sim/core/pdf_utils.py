from fpdf import FPDF
import datetime
import os

class DIANSimPDF(FPDF):
    def header(self):
        # Logo - Relativizado para el despliegue
        # Subir logo.png a app/assets/ en el repo
        base_dir = os.path.dirname(os.path.dirname(__file__))
        logo_path = os.path.join(base_dir, "app", "assets", "logo.png")
        
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 50)
        
        self.set_font('helvetica', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Reporte de Simulacro - DIAN Sim', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} | Generado el {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_exam_pdf(results_data, questions_details):
    """
    Genera un PDF con los resultados del simulacro.
    results_data: dict con total, correct, score, etc.
    questions_details: list de dicts con stem, user_ans, correct_key, rationale.
    """
    pdf = DIANSimPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Resumen Ejecutivo
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Resumen de Desempeño', 0, 1)
    
    score = results_data.get('score')
    if score is None and results_data.get('total', 0) > 0:
        score = (results_data.get('correct', 0) / results_data['total']) * 100
    
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, f"Puntaje Total: {score if score is not None else 0:.1f}%", 0, 1)
    pdf.cell(0, 10, f"Respuestas Correctas: {results_data.get('correct', 0)} de {results_data.get('total', 0)}", 0, 1)
    pdf.cell(0, 10, f"Puntos Ganados: +{results_data.get('points_earned', 0)}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Detalle de Preguntas', 0, 1)
    pdf.ln(5)
    
    def clean_text(text):
        if not text: return ""
        # Keep latin-1 (Spanish characters) but remove emojis/special symbols
        try:
            return str(text).encode('latin-1', 'ignore').decode('latin-1')
        except:
            return str(text).encode('ascii', 'ignore').decode('ascii')
    
    for i, q in enumerate(questions_details):
        is_right = q['user_ans'] == q['correct_key']
        color = (0, 128, 0) if is_right else (200, 0, 0) # Green or Red
        
        pdf.set_font('helvetica', 'B', 11)
        stem_clean = clean_text(q['stem'])
        pdf.multi_cell(0, 7, f"Pregunta {i+1}: {stem_clean[:150]}...")
        
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(*color)
        status = "CORRECTA" if is_right else "INCORRECTA"
        pdf.cell(0, 7, f"Estado: {status}", 0, 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Tu respuesta: {q['user_ans']} | Correcta: {q['correct_key']}", 0, 1)
        
        if q.get('rationale'):
            pdf.set_font('helvetica', 'I', 9)
            rationale_clean = clean_text(q['rationale'])
            pdf.multi_cell(0, 5, f"Justificación: {rationale_clean}")
        
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    import io
    raw_pdf = pdf.output()
    return io.BytesIO(bytes(raw_pdf))
