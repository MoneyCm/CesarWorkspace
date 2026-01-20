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
        
        # Try to initialize both if possible (for fallbacks)
        self.openai_client = None
        if self.provider == "openai":
            self.openai_client = openai.OpenAI(api_key=api_key)
        
        if self.provider == "gemini":
            genai.configure(api_key=api_key)
            
        if self.provider == "groq":
            self.openai_client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
    def generate_from_text(self, text: str, count: int = 5) -> List[dict]:
        # Increase context window to 10000 characters for better results
        context = text[:10000]
        
        prompt = f"""
        Actúa como un experto generador de preguntas de examen para la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia).
        Basándote en el siguiente texto, genera {count} preguntas de selección múltiple.

        IDIOMA OBLIGATORIO: ESPAÑOL (SPANISH).
        Todas las preguntas, opciones y justificaciones deben estar en completo y correcto español.
        SI EL TEXTO ORIGINAL ESTÁ EN INGLÉS, TRADUCE EL CONTEXTO Y GENERA LAS PREGUNTAS EN ESPAÑOL.

        Las preguntas deben evaluar comprensión, aplicación o análisis (no solo memoria).
        
        TEXTO A ANALIZAR:
        "{context}..."
        
        FORMATO DE SALIDA (Objeto JSON obligatorio):
        {{
          "questions": [
            {{
              "track": "FUNCIONAL | COMPORTAMENTAL | INTEGRIDAD",
              "competency": "nombre de la competencia",
              "topic": "tema específico",
              "stem": "Enunciado de la pregunta...",
              "options": {{
                "A": "Texto opción A",
                "B": "Texto opción B",
                "C": "Texto opción C"
              }},
              "correct_key": "A",
              "rationale": "Justificación técnica basada en el texto..."
            }}
          ]
        }}
        
        No incluyas texto fuera del objeto JSON. Solo JSON válido.
        """
        
        try:
            content = ""
            if self.provider == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            elif self.provider == "groq" and self.openai_client:
                # Groq es extremadamente rápido con Llama 3
                print(f"DEBUG: Enviando prompt a Groq (Llama 3.3)...")
                response = self.openai_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Actúa como un generador de JSON. Responde únicamente con el objeto JSON solicitado."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                print(f"DEBUG: Respuesta de Groq recibida (primeros 50 caracteres): {content[:50]}...")
                
            elif self.provider == "gemini":
                # Use absolute resource names for stability
                candidates = [
                    "models/gemini-1.5-flash", 
                    "models/gemini-1.5-flash-latest", 
                    "models/gemini-1.5-pro",
                    "models/gemini-2.0-flash-exp"
                ]
                
                print(f"DEBUG [v1.2.3]: Iniciando generación Gemini con candidatos: {candidates}")
                
                response = None
                last_error = None
                
                for model_name in candidates:
                    try:
                        print(f"DEBUG: Probando {model_name}...")
                        model = genai.GenerativeModel(model_name=model_name)
                        response = model.generate_content(prompt)
                        if response:
                            print(f"DEBUG: Éxito total con {model_name}")
                            break
                    except Exception as e:
                        error_str = str(e).lower()
                        print(f"DEBUG: Fallo en {model_name}: {str(e)}")
                        last_error = e
                        
                        # If it's a quota error, wait a bit before trying the next model
                        if "429" in error_str or "quota" in error_str:
                            print(f"DEBUG: Error de cuota detectado en {model_name}. Esperando 2 segundos...")
                            time.sleep(2)
                        
                        continue
                
                if not response:
                    # Final fallback to OpenAI if available
                    if self.openai_client:
                        print("DEBUG: Gemini agotado (Cuota). Intentando OpenAI (v1.2.3)...")
                        # Use OpenAI block directly to avoid recursive recursion issues if needed
                        response_oa = self.openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        content = response_oa.choices[0].message.content
                        if content:
                            print("DEBUG: Recuperado vía OpenAI.")
                        else:
                            raise Exception("Fallo en Gemini y OpenAI devolvió respuesta vacía.")
                    else:
                        error_msg = str(last_error)
                        if "limit: 0" in error_msg or "daily" in error_msg.lower():
                            raise Exception("CUOTA_DIARIA_AGOTADA: Has agotado el límite gratuito de Google por hoy. Espera 24h o usa OpenAI.")
                        raise Exception(f"CONEXION_FALLIDA_GEMINI_V123: {error_msg}")

                try:
                    content = response.text
                except Exception as e:
                    # Handle safety block or empty response
                    print(f"DEBUG: Error extracting text from response: {str(e)}")
                    if hasattr(response, 'candidates') and response.candidates:
                         # Try to see if there is any text at all
                         try:
                             content = response.candidates[0].content.parts[0].text
                         except:
                             raise Exception("La IA bloqueó la respuesta o devolvió un contenido vacío por seguridad.")
                    else:
                        raise Exception(f"No se pudo obtener texto de la respuesta: {str(e)}")

                # Cleanup markdown
                if "```json" in content:
                    content = content.replace("```json", "").split("```")[0]
                elif "```" in content:
                    content = content.replace("```", "")
        
            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise Exception(f"La IA devolvió un formato no válido: {str(e)}. Contenido: {content[:100]}...")

            # Extract candidates
            candidates = []
            if isinstance(data, dict):
                if "questions" in data:
                    candidates = data["questions"]
                elif len(data.keys()) == 1:
                    candidates = list(data.values())[0]
                else:
                    # Maybe it returned the first question as the root?
                    if "stem" in data:
                        candidates = [data]
            elif isinstance(data, list):
                candidates = data
                
            if not candidates or not isinstance(candidates, list):
                raise Exception("No se encontraron preguntas en la respuesta de la IA.")
                
            # Convert to internal Dict structure
            results = []
            for item in candidates:
                if not item.get("stem"):
                    continue
                    
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
                    "hash_norm": compute_hash(item.get("stem", ""))
                }
                results.append(q_dict)
                
            return results
            
        except Exception as e:
            raise Exception(f"Error en generación: {str(e)}")

