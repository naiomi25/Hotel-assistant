from typing import Dict, Any

from click import prompt
from app import state
from app.llm.llm import generate_response
from app.state.state import InitialState
from app.data_db.guests import GUESTS
from app.prompts.prompts import wellcome_prompt, initial_welcome_prompt

def nodo_guest_info(state: InitialState, room_number: str = None) -> InitialState:
    
    
    room_number = state.get("guest_info", {}).get("room")

    if not room_number:
        prompt = initial_welcome_prompt()
        ai_message = generate_response(prompt)
        state.setdefault("messages", [])
        state["messages"].append({"role": "assistant", "content": ai_message})
        state["assistant_message"] = ai_message
        return state

    
    guest_data = GUESTS.get(room_number)
    
    if not guest_data:
        message = f"No se encontró información para la habitación {room_number}. Por favor, acércate a recepción."
        state.setdefault("messages", [])
        state["messages"].append({"role": "assistant", "content": message})
        state["assistant_message"] = message
        return state

    # Actualizamos el estado con la info del huésped
    state["guest_info"]["name"] = guest_data["guest_name"]
    state["guest_info"]["has_children"] = guest_data["has_children"]

    prompt = wellcome_prompt(state)
    ai_message = generate_response(prompt)
    state["assistant_message"] = ai_message
    state.setdefault("messages", [])
    state["messages"].append({
        "role": "assistant",
        "content": ai_message
    })
    
    print(f"(paradebug) Bienvenido/a {guest_data['guest_name']} (habitación {room_number})!")
    print(f"(paradebug)Tiene hijos: {'Sí' if guest_data['has_children'] else 'No'}")
    print(f"(debug) Nodo GUEST INFO devuelve claves: {list(state.keys())}")
    return state