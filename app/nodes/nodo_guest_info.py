from typing import Dict, Any
from app.state.state import InitialState
from app.data_db.guests import GUESTS
from app.prompts.prompts import wellcome_prompt

def nodo_guest_info(state: InitialState) ->tuple[InitialState, str]:
    # Recogemos la info del front

    room_number = state.get("room")  # revisar esto con el endpoint

    if not room_number:
        print("No se proporcionó número de habitación.")
        return state, "No se proporcionó número de habitación"
    
    # comparamos con la bd mockeada
    guest_data = GUESTS.get(room_number)
    
    if not guest_data:
        print(f"No se encontró información para la habitación {room_number}.")
        return state, f"No se encontró información para la habitación {room_number}"
    
    # Actualizamos el estado con la info del huésped
    state["guest_info"] = {
        "name": guest_data["guest_name"],
        "room": room_number,
        "has_children": guest_data["has_children"],
    }

    message = wellcome_prompt(state)
    
    print(f" Bienvenido/a {guest_data['guest_name']} (habitación {room_number})!")
    print(f"Tiene hijos: {'Sí' if guest_data['has_children'] else 'No'}")
    
    return state, message