# visto

from typing import Dict, Any
from app.llm.llm import generate_response
from app.state.state import AgentState  # Usamos el nuevo AgentState
from app.data_db.guests import GUESTS
from app.prompts.prompts import welcome_prompt, initial_welcome_prompt
from langchain_core.messages import AIMessage


def nodo_guest_info(state: AgentState) -> AgentState:

    # def create_message_update(content: str,**extra_fields) -> dict:
    #      return {
    #          "messages": [AIMessage(content=content)],
    #          **extra_fields
    #      }

    room_number = state.get("guest_info", {}).get("room")

    if not room_number:
        ai_message = generate_response(initial_welcome_prompt())
        print(
            f"🏠 [DEBUG] nodo_guest_info: No hay habitación, devolviendo waiting_for_room=True"
        )
        return {
            "messages": [AIMessage(content=ai_message)],
            "guest_info": state.get("guest_info", {}),
            "waiting_for_room": True,
        }

    guest_data = GUESTS.get(room_number)

    if not guest_data:
        message = f"No se encontró información para la habitación {room_number}. Por favor, acércate a recepción."
        return {"messages": [AIMessage(content=message)]}

    # Actualizamos el estado con la info del huésped
    current_guest_info = state["guest_info"]
    current_guest_info["name"] = guest_data["guest_name"]
    current_guest_info["has_children"] = guest_data["has_children"]
    current_guest_info["room"] = room_number

    # 2. Generamos el mensaje
    ai_message = generate_response(welcome_prompt(state))

    print(
        f"(paradebug) Bienvenido/a {guest_data['guest_name']} (habitación {room_number})!"
    )
    print(f"(paradebug)Tiene hijos: {'Sí' if guest_data['has_children'] else 'No'}")
    print(f"(debug) Nodo GUEST INFO ejecutado.")

    # 3. Devolvemos las actualizaciones, incluyendo el mensaje y el guest_info actualizado
    return {
        "messages": [AIMessage(content=ai_message)],
        "guest_info": current_guest_info,
        "waiting_for_room": False,  # Ya tenemos la habitación
    }
