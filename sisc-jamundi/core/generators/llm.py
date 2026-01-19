import os
import json
import uuid
import datetime
import time
from typing import List
from db.models import Question
from core.dedupe import compute_hash
import openai
import google.generativeai as genai

class LLMGenerator:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider.lower()
        self.api_key = api_key
        
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=api_key)
        elif self.provider == "gemini":
            genai.configure(api_key=api_key)
            self.model = None # We will select model in generate step
            
    def generate_from_text(self, text: str, count: int = 5) -> List[dict]:
        prompt = f"""
        Actúa como un experto generador de preguntas de examen para la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia).
        Basándote en el siguiente texto, genera {count} preguntas de selección múltiple.

        IDIOMA OBLIGATORIO: ESPAÑOL (SPANISH).
        Todas las preguntas, opciones y justificaciones deben estar en completo y correcto español.
        SI EL TEXTO ORIGINAL ESTÁ EN INGLÉS, TRADUCE EL CONTEXTO Y GENERA LAS PREGUNTAS EN ESPAÑOL.

        Las preguntas deben evaluar comprensión, aplicación o análisis (no solo memoria).
        
        TEXTO A ANALIZAR:
        "{text[:3000]}..." (truncado si es muy largo)
        
        FORMATO DE SALIDA (Lista JSON estricta):
        [
            {{
                "track": "FUNCIONAL" | "COMPORTAMENTAL" | "INTEGRIDAD",
                "competency": "Competencia (En Español)",
                "topic": "Tema (En Español)",
                "stem": "Pregunta (En Español)...",
                "options": {{
                    "A": "Opción A (En Español)",
                    "B": "Opción B (En Español)",
                    "C": "Opción C (En Español)",
                    "D": "Opción D (En Español)"
                }},
                "correct_key": "A",
                "rationale": "Justificación (En Español)."
            }}
        ]
        
        No incluyas keys extra. Solo JSON válido.
        """
        
        content = ""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            elif self.provider == "gemini":
                # Dynamic model discovery
                chosen_model = None
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            if 'gemini' in m.name:
                                chosen_model = m.name
                                break
                except Exception as e:
                    # If listing fails, suppress and use fallbacks
                    pass

                candidates = []
                if chosen_model:
                    candidates.append(chosen_model)
                
                # Fallbacks with 'models/' prefix which is safer
                candidates.extend([
                    "models/gemini-1.5-flash", 
                    "models/gemini-1.5-flash-latest",
                    "models/gemini-1.5-pro",
                    "models/gemini-2.0-flash-exp"
                ])

                response = None
                last_error = None
                
                for model_name in candidates:
                    try:
                        print(f"DEBUG: Probando {model_name}...")
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response:
                            print(f"DEBUG: Éxito con {model_name}")
                            break # Success
                    except Exception as e:
                        error_str = str(e).lower()
                        print(f"DEBUG: Error en {model_name}: {str(e)}")
                        last_error = e
                        
                        if "429" in error_str or "quota" in error_str:
                            print("DEBUG: Detectado límite de cuota. Esperando para rotar...")
                            time.sleep(2)
                        continue
                
                if not response:
                    raise Exception(f"Failed to generate with all Gemini models. Last error: {str(last_error)}")

                content = response.text
                # Cleanup if markdown code blocks exist
                if "```json" in content:
                    content = content.replace("```json", "").replace("```", "")
        
            # Parse JSON
            data = json.loads(content)
            # Handle if wrapped in a key like "questions"
            if isinstance(data, dict):
                candidates = data.get("questions", [])
                if not candidates and len(data.keys()) == 1:
                     candidates = list(data.values())[0]
            elif isinstance(data, list):
                candidates = data
            else:
                candidates = []
                
            # Convert to internal Dict structure
            results = []
            for item in candidates:
                q_dict = {
                    "question_id": str(uuid.uuid4()),
                    "track": item.get("track", "FUNCIONAL"),
                    "competency": item.get("competency", "General"),
                    "topic": item.get("topic", "Generado por IA"),
                    "difficulty": 3,
                    "stem": item.get("stem"),
                    "options_json": item.get("options"),
                    "correct_key": item.get("correct_key"),
                    "rationale": item.get("rationale"),
                    "source_refs": "Generado desde Texto Usuario",
                    "created_at": datetime.datetime.utcnow(),
                    "hash_norm": compute_hash(item.get("stem", ""))
                }
                results.append(q_dict)
                
            return results
            
        except Exception as e:
            error_msg = str(e)
            if "limit: 0" in error_msg:
                error_msg = "CUOTA_DIARIA_AGOTADA: Límite diario de Gemini alcanzado. Intenta mañana o usa OpenAI."
            # Re-raise exception to be handled by UI
            raise Exception(f"{error_msg}")
