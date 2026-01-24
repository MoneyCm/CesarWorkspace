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
    def __init__(self, provider: str, api_key: str, model_name: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        
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
            
    def generate_from_text(self, text: str, count: int = 5, difficulty: int = 2) -> List[dict]:
        """Generates questions by splitting into smaller chunks for reliability."""
        all_results = []
        batch_size = 5 # Reliable size for JSON generation
        
        remaining = count
        while remaining > 0:
            current_batch = min(remaining, batch_size)
            print(f"DEBUG: Generating batch of {current_batch} questions (Remaining: {remaining})...")
            try:
                batch_results = self._generate_batch(text, current_batch, difficulty)
                all_results.extend(batch_results)
                remaining -= current_batch
                # Small delay to avoid aggressive rate limits in some providers
                if remaining > 0:
                    time.sleep(1)
            except Exception as e:
                # If we have some results already, return them instead of failing completely
                if all_results:
                    print(f"WARNING: Generation interrupted, but returning {len(all_results)} questions already generated. Error: {e}")
                    break
                else:
                    raise e
                    
        return all_results

    def _generate_batch(self, text: str, count: int = 5, difficulty: int = 2) -> List[dict]:
        # Increase context window to 10000 characters for better results
        context = text[:10000]
        
        prompt = f"""
        Actúa como un experto generador de preguntas de examen para la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia).
        Basándote en el siguiente texto, genera EXACTAMENTE {count} preguntas de selección múltiple con un nivel de DIFICULTAD: {difficulty} (donde 1=Básico, 2=Intermedio, 3=Avanzado).

        REQUISITO CRÍTICO - PREGUNTAS SITUACIONALES: 
        DEBES crear situaciones de la vida real o casos hipotéticos. NO hagas preguntas que se respondan con solo recordar una definición. El usuario debe ANALIZAR y APLICAR el conocimiento al caso planteado.

        EJEMPLO DE FORMATO DESEADO:
        - STEM: "SITUACIÓN: Un contribuyente presenta su declaración fuera de término alegando fallas técnicas, pero no hay reporte de contingencia oficial. PREGUNTA: ¿Cuál es el procedimiento que usted, como gestor de impuestos, debe aplicar?"
        - OPCIONES: {{"A": "Sanción por extemporaneidad según el Estatuto.", "B": "Aceptar la justificación sin pruebas.", "C": "Anular la declaración sin previo aviso."}}

        IDIOMA OBLIGATORIO: ESPAÑOL.
        
        TEXTO A ANALIZAR:
        "{context}..."
        
        FORMATO DE SALIDA (Objeto JSON obligatorio):
        {{
          "questions": [
            {{
              "track": "FUNCIONAL | COMPORTAMENTAL | INTEGRIDAD",
              "competency": "nombre de la competencia",
              "topic": "tema específico",
              "difficulty": {difficulty},
              "stem": "SITUACIÓN: [Caso detallado]. PREGUNTA: [Enunciado táctico]...",
              "options": {{
                "A": "Acción/Respuesta A",
                "B": "Acción/Respuesta B",
                "C": "Acción/Respuesta C"
              }},
              "correct_key": "A",
              "rationale": "Justificación técnica basada específicamente en la norma aplicada al caso..."
            }}
          ]
        }}
        
        IMPORTANTE: No respondas con nada que no sea el JSON. Asegúrate de que el campo 'stem' SIEMPRE empiece con 'SITUACIÓN:'.
        """
        
        try:
            content = ""
            if self.provider == "openai" and self.openai_client:
                model = self.model_name if self.model_name else "gpt-4o-mini"
                print(f"DEBUG: Enviando lote a OpenAI ({model})...")
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            elif self.provider == "groq" and self.openai_client:
                # Groq es extremadamente rápido con Llama 3
                print(f"DEBUG: Enviando lote a Groq (Llama 3.3)...")
                response = self.openai_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Actúa como un generador de JSON. Responde únicamente con el objeto JSON solicitado."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            elif self.provider == "gemini":
                # Use model names directly (SDK handles them better without models/ prefix sometimes)
                if self.model_name:
                    clean_name = self.model_name.replace("models/", "")
                    candidates = [clean_name, "models/" + clean_name]
                else:
                    candidates = [
                        "gemini-1.5-flash", 
                        "gemini-1.5-pro",
                        "gemini-1.5-flash-latest"
                    ]
                
                response = None
                last_error = None
                
                for model_name in candidates:
                    try:
                        print(f"DEBUG: Enviando lote a Gemini ({model_name})...")
                        model = genai.GenerativeModel(model_name=model_name)
                        response = model.generate_content(prompt)
                        if response:
                            break
                    except Exception as e:
                        error_str = str(e).lower()
                        last_error = e
                        if "429" in error_str or "quota" in error_str:
                            print(f"DEBUG: Quota hit for {model_name}, waiting...")
                            time.sleep(3)
                        continue
                
                if not response:
                    # Specific message for Google API Quota
                    if "429" in str(last_error) or "quota" in str(last_error).lower():
                        raise Exception("Límite de cuota de Google Gemini alcanzado (Free Tier). Por favor, intenta generar menos preguntas a la vez o espera 60 segundos para que se reinicie tu ventana de peticiones por minuto.")
                    
                    # Final fallback to OpenAI if available
                    if self.openai_client and self.provider != "gemini": # only if it's a multi-provider context
                        response_oa = self.openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        content = response_oa.choices[0].message.content
                    else:
                        raise Exception(f"Fallo en generación Gemini del lote: {last_error}")

                try:
                    if not content:
                        content = response.text
                except Exception:
                    if hasattr(response, 'candidates') and response.candidates:
                         try:
                             content = response.candidates[0].content.parts[0].text
                         except:
                             raise Exception("La IA bloqueó la respuesta del lote por seguridad.")
                    else:
                        raise Exception("No se pudo obtener texto de la respuesta del lote.")

                # Cleanup markdown
                if "```json" in content:
                    content = content.replace("```json", "").split("```")[0]
                elif "```" in content:
                    content = content.replace("```", "")
        
            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                # Attempt to clean common errors
                content = content.replace("'", '"') # risky but common Fix
                try:
                    data = json.loads(content)
                except:
                    raise Exception(f"Error de sintaxis JSON en el lote: {str(e)}")

            # Extract candidates
            candidates = []
            if isinstance(data, dict):
                if "questions" in data:
                    candidates = data["questions"]
                elif len(data.keys()) == 1:
                    candidates = list(data.values())[0]
                else:
                    if "stem" in data:
                        candidates = [data]
            elif isinstance(data, list):
                candidates = data
                
            if not candidates or not isinstance(candidates, list):
                raise Exception("No se encontraron preguntas en la respuesta del lote.")
                
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
                    "difficulty": item.get("difficulty", difficulty),
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
            error_msg = str(e)
            if "429" in error_msg or "rate_limit_exceeded" in error_msg:
                if self.provider == "groq":
                    raise Exception("Límite diario de Groq alcanzado (TPD). Por favor, espera a que se reinicie tu cuota o usa Google Gemini como alternativa gratuita más estable.")
                else:
                    raise Exception(f"Límite de velocidad (Rate Limit) alcanzado: {error_msg}")
            raise Exception(f"Fallo en lote: {error_msg}")

    def explain_question(self, question_data: dict) -> str:
        """Provides a socratic and educational explanation for a question."""
        prompt = f"""
        Actúa como un Tutor Experto de la DIAN. Tu objetivo es explicar la lógica detrás de la siguiente pregunta de examen sin revelar la respuesta correcta directamente si es posible, o guiando al estudiante a través del razonamiento legal.
        
        CASO/SITUACIÓN: {question_data.get('stem')}
        OPCIONES DISPONIBLES: {question_data.get('options_json')}
        RESPUESTA CORRECTA (para tu referencia): {question_data.get('correct_key')}
        JUSTIFICACIÓN TÉCNICA: {question_data.get('rationale')}
        
        INSTRUCCIONES PARA EL TUTOR:
        1. Sé pedagógico y cercano.
        2. Explica la norma o concepto legal involucrado.
        3. Ayuda a descartar las opciones incorrectas basándote en la lógica del caso.
        4. No digas simplemente "La respuesta es A". Di algo como "En este escenario, debemos observar que la norma X indica Y... por lo tanto..."
        5. Mantén la explicación concisa (máximo 2 párrafos).
        
        IDIOMA: ESPAÑOL.
        """
        
        try:
            if self.provider == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
                
            elif self.provider == "groq" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
                
            elif self.provider == "gemini":
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
                
            return "No se pudo conectar con el proveedor de IA para la explicación."
        except Exception as e:
            return f"El tutor tuvo un pequeño problema: {str(e)}"


