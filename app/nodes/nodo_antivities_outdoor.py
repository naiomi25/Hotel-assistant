# visto 
from typing import Dict, Any
from app.llm.llm import generate_response
from app.prompts.prompts import  activities_prompt_outdoor
from app.state.state import AgentState

from app.data_db.all_activities import all_activities
from langchain_core.messages import AIMessage

def nodo_activities_outdoor(state: AgentState) -> AgentState:
    
    available_activities = [
        a for a in all_activities
        if a["weather"] == state["weather_filter"]
        and a["has_children"] == state["guest_info"]["has_children"]
    ]
    state["available_activities"] = [a["name"] for a in available_activities]

    

    print("☀️ Nodo ACTIVIDADES OUTDOOR ejecutado")
    prompt = activities_prompt_outdoor(state)
    ai_message = generate_response(prompt)
    return {
        "messages": [AIMessage(content=ai_message)],
        "available_activities": state["available_activities"],
        # Establecemos un flag para que el front-end sepa que debe mostrar botones de selección
        "waiting_for_selection": True 
    }