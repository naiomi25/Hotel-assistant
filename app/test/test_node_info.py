from app.nodes.nodo_guest_info import nodo_guest_info

state = {
    "room": "101",
    "guest_info": None,
    "weather": None,
    "selected_activities": [],
    "available_activities": [],
    "unavailable_activities": [],
    "city_activities": [],
    "final_choice": None,
}

new_state = nodo_guest_info(state)
print("Estado actualizado:", new_state)