from typing import Dict, Any
from app.state.state import InitialState
from app.services.api_weather import api_weather

def nodo_weather(state: InitialState) -> Dict[str, Any]:
    weather_data = api_weather()
    state["weather"] = {
        "description": weather_data["description"],
        "temperature": weather_data["temp"]
    }

    print(f"🌤 Clima actual en Tenerife: {state['weather']['description']}, {state['weather']['temperature']}°C")
    return state