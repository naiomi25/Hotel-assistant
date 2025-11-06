from typing import Dict, Any
from app.llm.llm import generate_response
from app.prompts.prompts import activities_prompt
from app.state import state
from app.state.state import InitialState
from app.data_db.all_activities import all_activities


def nodo_activities(state: InitialState) -> tuple[InitialState, str]:
    
    available_activities = [
        a for a in all_activities
        if (a["weather"] == state["weather_filter"])
        and (state["guest_info"]["has_children"] == a["has_children"])
    ]
    unavailable_activities = [
        a["name"] for a in all_activities if a not in available_activities
    ]
    state["available_activities"] = [a["name"] for a in available_activities]
    state["unavailable_activities"] = unavailable_activities
    
    
    prompt = activities_prompt(state)
    ai_message = generate_response(prompt)

    return state, ai_message