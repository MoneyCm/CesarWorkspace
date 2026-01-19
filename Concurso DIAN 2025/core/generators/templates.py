import random
import uuid
import datetime
from core.dedupe import compute_hash
from core.schemas import QuestionCreate

TRACKS = ["FUNCIONAL", "COMPORTAMENTAL", "INTEGRIDAD"]

COMPETENCIES = {
    "FUNCIONAL": ["Tributaria", "Aduanera", "Cambiaria", "Derecho Administrativo"],
    "COMPORTAMENTAL": ["Trabajo en Equipo", "Liderazgo", "Orientación al Logro", "Servicio al Ciudadano"],
    "INTEGRIDAD": ["Ética Pública", "Código Disciplinario", "Transparencia"]
}

TOPICS = {
    "Tributaria": ["Impuesto sobre la Renta", "IVA", "Facturación Electrónica", "Retención en la Fuente"],
    "Aduanera": ["Aranceles", "Importaciones", "Exportaciones", "Régimen Sancionatorio"],
    "Cambiaria": ["Declaración de Cambio", "Canalización de Divisas", "Infracciones"],
    "Derecho Administrativo": ["Función Pública", "Contratación Estatal", "Actos Administrativos"],
    "Trabajo en Equipo": ["Resolución de Conflictos", "Comunicación Asertiva", "Colaboración"],
    "Liderazgo": ["Toma de Decisiones", "Motivación", "Delegación"],
    "Orientación al Logro": ["Metas", "Indicadores de Gestión", "Mejora Continua"],
    "Servicio al Ciudadano": ["PQRS", "Atención al Usuario", "Lenguaje Claro"],
    "Ética Pública": ["Conflictos de Interés", "Valores del Servicio Público"],
    "Código Disciplinario": ["Faltas Graves", "Sanciones", "Deberes"],
    "Transparencia": ["Acceso a la Información", "Rendición de Cuentas"]
}

TEMPLATES = [
    {
        "text": "En el contexto de {topic}, ¿cuál de las siguientes situaciones describe mejor el concepto de {concept}?",
        "options": [
            "Definición precisa y ajustada a la normativa vigente.",
            "Definición vaga que podría confundirse con otros términos.",
            "Definición que corresponde a un concepto opuesto.",
            "Afirmación que no tiene relevancia directa con el tema."
        ],
        "correct": "A"
    },
    {
        "text": "Un funcionario de la DIAN se enfrenta a un caso de {topic}. Según la normativa vigente, la acción prioritaria debería ser:",
        "options": [
            "Realizar el procedimiento estándar establecido en la ley.",
            "Consultar informalmente sin dejar registro escrito.",
            "Proponer una solución alternativa no regulada.",
            "Ignorar el caso hasta recibir instrucciones superiores."
        ],
        "correct": "A"
    },
    {
        "text": "Para asegurar {topic} de manera efectiva en un equipo de trabajo, ¿qué estrategia es la más adecuada?",
        "options": [
            "Implementar mecanismos de seguimiento y retroalimentación constante.",
            "Imponer reglas estrictas sin consultar al equipo.",
            "Dejar que cada funcionario actúe según su criterio personal.",
            "Delegar la responsabilidad sin supervisión alguna."
        ],
        "correct": "A"
    }
]

CONCEPTS = {
    "Impuesto sobre la Renta": ["Renta Líquida Gravable", "Deducciones", "Rentas Exentas", "Patrimonio Bruto"],
    "IVA": ["Hecho Generador", "Bienes Exentos", "Bienes Excluidos", "Prorrateo"],
    "Facturación Electrónica": ["Validación Previa", "Documento Soporte", "Notas Crédito", "Contingencia"],
    "Retención en la Fuente": ["Agente Retenedor", "Base Gravable", "Tarifa", "Autorretención"],
    "Aranceles": ["Clasificación Arancelaria", "Ad Valorem", "Nomenclatura", "Gravamen"],
    "Importaciones": ["Declaración de Importación", "Levante", "Abandono Legal", "Tributos Aduaneros"],
    "Exportaciones": ["DEX", "Reembarque", "Zonas Francas", "Certificado de Origen"],
    "Régimen Sancionatorio": ["Extemporaneidad", "Corrección", "Inexactitud", "Clausura del Establecimiento"],
    "Declaración de Cambio": ["Formulario No. 1", "Operaciones de Cambio", "Canalización", "IMC"],
    "Canalización de Divisas": ["Mercado Cambiario", "Cuentas de Compensación", "Intermediarios", "Reintegro"],
    "Infracciones": ["Lavado de Activos", "Contrabando", "Déficit Cambiario", "Sanción Reducida"],
    "Función Pública": ["Carrera Administrativa", "Mérito", "Evaluación de Desempeño", "Situaciones Administrativas"],
    "Contratación Estatal": ["Licitación Pública", "Selección Abreviada", "Concurso de Méritos", "Contratación Directa"],
    "Actos Administrativos": ["Motivación", "Notificación", "Firmeza", "Revocatoria Directa"],
    "Resolución de Conflictos": ["Mediación", "Negociación", "Asertividad", "Escucha Activa"],
    "Comunicación Asertiva": ["Empatía", "Claridad", "Respeto", "Feedback"],
    "Colaboración": ["Sinergia", "Objetivos Comunes", "Confianza", "Delegación"],
    "Toma de Decisiones": ["Análisis de Riesgos", "Criterio Técnico", "Oportunidad", "Consenso"],
    "Motivación": ["Reconocimiento", "Clima Laboral", "Estímulos", "Sentido de Pertenencia"],
    "Delegación": ["Empoderamiento", "Control", "Responsabilidad", "Instrucciones Claras"],
    "Metas": ["SMART", "Planes de Acción", "Cronograma", "Resultado Esperado"],
    "Indicadores de Gestión": ["Eficiencia", "Eficacia", "Efectividad", "Línea Base"],
    "Mejora Continua": ["Ciclo PHVA", "Acciones Correctivas", "Autocontrol", "Auditoría"],
    "PQRS": ["Derecho de Petición", "Términos de Respuesta", "Petición Anónima", "Queja vs Reclamo"],
    "Atención al Usuario": ["Canales de Atención", "Protocolo", "Accesibilidad", "Satisfacción"],
    "Lenguaje Claro": ["Simplicidad", "Estructura", "Diseño", "Comprensión"],
    "Conflictos de Interés": ["Imparcialidad", "Declaración", "Impedimentos", "Recusaciones"],
    "Valores del Servicio Público": ["Honestidad", "Respeto", "Compromiso", "Diligencia"],
    "Faltas Graves": ["Dolo", "Culpa Gravísima", "Abuso de Función", "Acoso Laboral"],
    "Sanciones": ["Destitución", "Suspensión", "Multa", "Inhabilidad"],
    "Deberes": ["Cumplimiento", "Custodia", "Trato Respetuoso", "Denuncia"],
    "Acceso a la Información": ["Transparencia Activa", "Transparencia Pasiva", "Datos Abiertos", "Reserva Legal"],
    "Rendición de Cuentas": ["Diálogo", "Informes de Gestión", "Audiencia Pública", "Veeduría"]
}

def generate_dummy_questions(count: int = 50) -> list[dict]:
    questions = []
    
    for _ in range(count):
        track = random.choice(TRACKS)
        competency = random.choice(COMPETENCIES[track])
        topic = random.choice(TOPICS.get(competency, ["General"]))
        
        template = random.choice(TEMPLATES)
        
        # Select a realistic concept based on topic
        if topic in CONCEPTS:
            concept_var = random.choice(CONCEPTS[topic])
        else:
             concept_var = "Concepto General"

        stem = template["text"].format(topic=topic, concept=concept_var)
        
        # Shuffle options
        opts = template["options"][:]
        # We need to track which one is correct after shuffle
        # For simplicity in this dummy generator, let's fix the shuffle or track it carefully
        # Simple approach: A is always correct in template, we map it
        
        correct_content = opts[0]
        random.shuffle(opts)
        
        options_map = {
            "A": opts[0],
            "B": opts[1],
            "C": opts[2],
            "D": opts[3]
        }
        
        # Find which key holds the correct content
        correct_key =  next(k for k, v in options_map.items() if v == correct_content)
        
        q_dict = {
            "question_id": str(uuid.uuid4()),
            "track": track,
            "competency": competency,
            "topic": topic,
            "difficulty": random.randint(1, 5),
            "stem": stem,
            "options_json": options_map,
            "correct_key": correct_key,
            "rationale": f"La respuesta correcta es {correct_key} porque se alinea con los principios de {topic} y aborda adecuadamente el concepto de {concept_var}.",
            "source_refs": "Estatuto Tributario / Guía DIAN",
            "created_at": datetime.datetime.utcnow(),
            "hash_norm": compute_hash(stem)
        }
        questions.append(q_dict)
        
    return questions
