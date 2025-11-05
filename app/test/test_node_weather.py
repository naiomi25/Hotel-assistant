from app.nodes.nodo_weather import nodo_weather

# Estado inicial de prueba
state = {
    "room": "101",
    "guest_name": "Prueba",
    "has_children": True,
    "weather": None,
    "selected_activities": [],
    "available_activities": [],
    "unavailable_activities": [],
    "city_activities": [],
    "final_choice": "",
}

# Llamamos al nodo de weather
updated_state = nodo_weather(state)

# Imprimimos el estado actualizado
print(updated_state)