import os
from dotenv import load_dotenv

load_dotenv()


def gemini_explanation(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "No se encontró GEMINI_API_KEY. Crea un archivo .env con GEMINI_API_KEY=TU_API_KEY_AQUI"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            "Responde como tutor de química orgánica, con explicación clara y académica:\n\n" + prompt
        )
        return response.text
    except Exception as e:
        return f"Error al consultar Gemini: {e}"
