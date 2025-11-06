import os       
import requests
from app.config.settings import OPENWEATHER_API_KEY
from app.config.api_endpoints import OPENWEATHER_API_URL


Tenerife = {"lat": 28.4682, "lon": -16.2546}

def api_weather():
    
    coords = Tenerife  
    
    if not OPENWEATHER_API_KEY:
        raise ValueError("❌ Falta la API key de OpenWeatherMap en settings o .env")
    
    url = (
        f"{OPENWEATHER_API_URL}"
        f"?lat={coords['lat']}&lon={coords['lon']}"
        f"&appid={OPENWEATHER_API_KEY}&units=metric&lang=es"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

      
        description = data["weather"][0]["description"]
        temperature = round(data["main"]["temp"])
        
    #    tenemos que mapear el clima a "sol" o "lluvia" para filtrar actividades
        
        if "lluvia" in description or "tormenta" in description:
            weather_filter = "indoor"
        else:
            weather_filter = "outdoor"

        # devolvemos la description tal cual para el prompt y el filtro para las actividades
        
        return {"description": description, "temp": temperature, "weather_filter": weather_filter}
            
            
    except requests.RequestException as e:
        print(f"⚠️ Error al obtener el clima: {e}")
        return {
          
            "description": "No se pudo obtener el clima",
            "temp": None,
            "weather_filter": "indoor",
        }

