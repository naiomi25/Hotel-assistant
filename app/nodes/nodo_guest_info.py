from typing import Dict, Any

from click import prompt
from app.llm.llm import generate_response
from app.state.state import InitialState
from app.data_db.guests import GUESTS
from app.prompts.prompts import wellcome_prompt, initial_welcome_prompt

def nodo_guest_info(state: InitialState, room_number: str = None) -> tuple[InitialState, str]:
    
    if not room_number:
        prompt = initial_welcome_prompt()
        ai_message = generate_response(prompt)
        return state, ai_message

    state["guest_info"]["room"] = room_number
    guest_data = GUESTS.get(room_number)
    
    if not guest_data:
        message = f"No se encontró información para la habitación {room_number}. Por favor, acércate a recepción."
        return state, message

    # Actualizamos el estado con la info del huésped
    state["guest_info"]["name"] = guest_data["guest_name"]
    state["guest_info"]["has_children"] = guest_data["has_children"]

    prompt = wellcome_prompt(state)
    ai_message = generate_response(prompt)
    
    print(f"(paradebug) Bienvenido/a {guest_data['guest_name']} (habitación {room_number})!")
    print(f"(paradebug)Tiene hijos: {'Sí' if guest_data['has_children'] else 'No'}")

    return state, ai_message