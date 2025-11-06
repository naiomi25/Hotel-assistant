from typing import Dict, Any
from app.llm.llm import generate_response
from app.prompts.prompts import  activities_prompt_outdoor
from app.state import state
from app.state.state import InitialState
from app.data_db.all_activities import all_activities

def nodo_activities_outdoor(state: InitialState) -> InitialState:
    
    available_activities = [
        a for a in all_activities
        if a["weather"] == state["weather_filter"]
        and a["has_children"] == state["guest_info"]["has_children"]
    ]
    unavailable_activities = [a["name"] for a in all_activities if a not in available_activities]
        
    
    state["available_activities"] = [a["name"] for a in available_activities]
    state["unavailable_activities"] = unavailable_activities

    print("☀️ Nodo ACTIVIDADES OUTDOOR ejecutado")
    prompt = activities_prompt_outdoor(state)
    ai_message = generate_response(prompt)
    state["assistant_message"] = ai_message
    state.setdefault("messages", [])
    state["messages"].append({
        "role": "assistant",
        "content": ai_message
    })
    print(f"(debug) Nodo ACTIVIDADES OUTDOOR devuelve claves: {list(state.keys())}")
    return state