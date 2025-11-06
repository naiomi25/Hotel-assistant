from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather
from app.state.state import InitialState
from app.data_db.guests import GUESTS
from app.nodes.nodo_activities import nodo_activities
  


def create_test_state() -> InitialState:
    return {
        "room": "101",  # Habitación de prueba
        "guest_name": "",
        "has_children": False,
        "weather": None,
        "weather_description": "",
        "weather_filter": "",
        "selected_activities": [],
        "available_activities": [],
        "unavailable_activities": [],
        "city_activities": [],
        "final_choice": "",
    }

state = create_test_state()
state , message = nodo_guest_info(state)

state = nodo_weather(state)
print(f"\nClima actual:\nDescripción: {state['weather_description']}\nFilter: {state['weather_filter']}")
state, message = nodo_activities(state)
print("Estado final después de ambos nodos:", state)
print("\nMensaje de actividades:\n", message)

