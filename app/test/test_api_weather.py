import os
from dotenv import load_dotenv

load_dotenv()

# Test para ver si se carga la API de Weather correctamente

api_key = os.getenv("OPENWEATHER_API_KEY")


if api_key:
    print(f"✅ La API Key se leyó correctamente: {api_key[:4]}...")  # Solo mostramos los primeros 4 caracteres por seguridad
else:
    print("❌ No se pudo leer la API Key. Revisa tu .env")
