from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather
from app.state.state import InitialState
from app.data.guests import GUESTS


def create_test_state() -> InitialState:
    return {
        "room": "101",  # Habitación de prueba
        "guest_name": "",
        "has_children": False,
        "weather": None,
        "selected_activities": [],
        "available_activities": [],
        "unavailable_activities": [],
        "city_activities": [],
        "final_choice": "",
    }

state = create_test_state()
state = nodo_guest_info(state)
state = nodo_weather(state)
print
("Estado final después de ambos nodos:", state)
