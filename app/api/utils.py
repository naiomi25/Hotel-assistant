"""
Utilidades compartidas para las rutas de la API
"""

import re
from app.state.state import initial_state
from langchain_core.messages import HumanMessage


def extract_room_number(text: str) -> str:
    """Extrae el número de habitación del mensaje del usuario."""
    match = re.search(r"\b\d{3,4}\b", text)
    return match.group() if match else None


def messages_to_json(messages):
    """Convierte objetos LangChain Messages en dicts simples."""
    serialized = []
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        serialized.append({"role": role, "content": content})
    return serialized


def _get_full_state(current_state, user_message=None):
    """Construye el estado completo para LangGraph."""
    base_state = {
        "guest_info": current_state.get("guest_info", initial_state()["guest_info"]),
        "weather": current_state.get("weather", ""),
        "weather_description": current_state.get("weather_description", ""),
        "weather_filter": current_state.get("weather_filter", ""),
        "selected_activities": current_state.get("selected_activities", []),
        "available_activities": current_state.get("available_activities", []),
        "unavailable_activities": current_state.get("unavailable_activities", []),
        "city_activities": current_state.get("city_activities", []),
        "final_choice": current_state.get("final_choice", ""),
        "city_guide": current_state.get("city_guide"),
        "waiting_for_selection": current_state.get("waiting_for_selection", False),
        "waiting_for_room": current_state.get("waiting_for_room", False),
        "waiting_for_transport": current_state.get("waiting_for_transport", False),
        "transport_response": current_state.get("transport_response"),
        "human_response": current_state.get("human_response"),
        "session_id": current_state.get("session_id"),
    }

    current_messages = current_state.get("messages", [])
    if user_message:
        base_state["messages"] = current_messages + [HumanMessage(content=user_message)]
    else:
        base_state["messages"] = current_messages

    return base_state
