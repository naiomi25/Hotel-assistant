from app.state.state import AgentState
from app.services.api_weather import api_weather

def nodo_weather(state: AgentState) -> AgentState:
    weather_data = api_weather()
    
    weather_update = {
        "weather_description": weather_data["description"], 
        "weather_filter": weather_data["weather_filter"], 
        "weather": weather_data["temp"], 
    }

    print(f"🌤 Clima actual en Tenerife: {weather_update['weather_description']}, {weather_update['weather']}°C")
    print(f"(debug) Nodo WEATHER ejecutado.")
    
    return weather_update