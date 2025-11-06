from typing import Dict, Any
from app.state.state import InitialState
from app.services.api_weather import api_weather

def nodo_weather(state: InitialState) -> Dict[str, Any]:
    weather_data = api_weather()
    state["weather_description"] = weather_data["description"]  
    state["weather_filter"] = weather_data["weather_filter"]    
    state["weather"] = weather_data["temp"]   

    print(f"🌤 Clima actual en Tenerife: {state['weather_description']}, {state['weather']}°C")
    return state