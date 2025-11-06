from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather
from app.state.state import InitialState
from app.data_db.guests import GUESTS
from app.nodes.nodo_activities import nodo_activities
  


def create_test_state() -> InitialState:
    return {
        "guest_info": {"name": "", "room": "", "has_children": False},
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
state , ai_message = nodo_guest_info(state)
print("\n🟦 Mensaje inicial:")
print(ai_message)
room_number = "101"
state , ai_message = nodo_guest_info(state, room_number)
print("\n🟩 Mensaje tras introducir la habitación:")
print(ai_message)
state = nodo_weather(state)
print(f" \n🌤 (debug)\nClima actual:\nDescripción: {state['weather_description']}\nFilter: {state['weather_filter']}")
state, ai_message = nodo_activities(state)
print("\n🎯 (debug) Estado final después de ambos nodos:", state)
print("\n 💬 (debug) Mensaje de actividades:\n", ai_message)

