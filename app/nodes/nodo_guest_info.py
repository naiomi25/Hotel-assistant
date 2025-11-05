from typing import Dict, Any
from app.state.state import InitialState
from app.data.guests import GUESTS

def nodo_guest_info(state: InitialState) -> InitialState:
    # Recogemos la info del front
    
    room_number = state.get("room")
    
    if not room_number:
        print("No se proporcionó número de habitación.")
        return state
    
    # comparamos con la bd mockeada
    guest_data = GUESTS.get(room_number)
    
    if not guest_data:
        print(f"No se encontró información para la habitación {room_number}.")
        return state
    
    # Actualizamos el estado con la info del huésped
    state["guest_info"] = {
        "name": guest_data["guest_name"],
        "room": room_number,
        "has_children": guest_data["has_children"],
    }

    print(f" Bienvenido/a {guest_data['guest_name']} (habitación {room_number})!")
    print(f"Tiene hijos: {'Sí' if guest_data['has_children'] else 'No'}")
    return state