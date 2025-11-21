# --- INTEGRACIÓN GEMINI ---
import google.generativeai as genai
import google.cloud.vision
from google.cloud import vision
import base64
import requests
from django.conf import settings
import openai

# Usa tu API Key de Gemini
API_KEY = "AIzaSyCgN-Q9ozME_wk7t839tSavXlYOVrzvxWo"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-pro")

# API Key de OpenAI
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

def get_agriculture_answer(question: str, crop_info: dict | None = None) -> dict:
    """
    Consulta a Gemini para preguntas agrícolas y genera imágenes reales con DALL-E si lo pide.
    Retorna dict con keys: ok(bool), answer(str), source(str), image_url(str|None)
    """
    prompt = question.strip() if question else ""
    if crop_info:
        prompt += f"\nContexto: cultivo={crop_info.get('name')}, lat={crop_info.get('lat')}, lon={crop_info.get('lon')}"

    image_keywords = ["imagen", "foto", "dibuja", "genera una imagen", "visualiza", "picture", "draw", "generate an image", "show me a picture"]
    wants_image = any(kw in prompt.lower() for kw in image_keywords)

    def generate_dalle_image(query):
        try:
            response = openai.Image.create(
                prompt=query,
                n=1,
                size="512x512"
            )
            import sys
            print("DALL-E response:", response, file=sys.stderr)
            return response['data'][0]['url'] if response and 'data' in response and response['data'] else None
        except Exception as e:
            import sys
            print("DALL-E error:", e, file=sys.stderr)
            return None

    try:
        if wants_image:
            tema = prompt.split("imagen de")[-1].strip() if "imagen de" in prompt else prompt
            image_url = generate_dalle_image(tema)
            answer = "Aquí tienes una imagen generada por IA."
            return {"ok": True, "answer": answer, "source": "dalle", "image_url": image_url}
        else:
            response = model.generate_content(prompt)
            return {"ok": True, "answer": response.text, "source": "gemini", "image_url": None}
    except Exception as e:
        return {"ok": False, "answer": f"Error de red al contactar IA: {str(e)}", "source": "gemini", "image_url": None}


def recommend_sowing_window(lat: float, lon: float, crop_name: str) -> dict:
    """
    Recomienda ventana de siembra usando Gemini.
    """
    prompt = f"Recomienda la mejor ventana de siembra para {crop_name} en lat={lat}, lon={lon}. Indica meses ideales y consideraciones climáticas."
    try:
        response = model.generate_content(prompt)
        return {"ok": True, "window_text": response.text, "source": "gemini"}
    except Exception as e:
        return {"ok": False, "window_text": f"Error de red al contactar IA: {str(e)}", "source": "gemini"}


def recommend_sowing_window(lat: float, lon: float, crop_name: str) -> dict:
    """
    Recomienda ventana de siembra usando Gemini.
    """
    prompt = f"Recomienda la mejor ventana de siembra para {crop_name} en lat={lat}, lon={lon}. Indica meses ideales y consideraciones climáticas."
    try:
        response = model.generate_content(prompt)
        return {"ok": True, "window_text": response.text, "source": "gemini"}
    except Exception as e:
        return {"ok": False, "window_text": f"Error de red al contactar IA: {str(e)}", "source": "gemini"}
