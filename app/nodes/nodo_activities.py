# visto
from typing import Dict, Any
from app.llm.llm import generate_response
from app.prompts.prompts import  activities_prompt_indoor
from app.data_db.all_activities import all_activities
from app.state.state import AgentState
from langchain_core.messages import AIMessage


def nodo_activities(state: AgentState) -> AgentState:

    available_activities = [
        a for a in all_activities
        if (a["weather"] == state["weather_filter"])
        and a["has_children"] == state["guest_info"]["has_children"]
    ]
    
    state["available_activities"] = [a["name"] for a in available_activities]
   
    
    print("☀️ Nodo ACTIVIDADES inTDOOR ejecutado")
    prompt = activities_prompt_indoor(state)
    ai_message = generate_response(prompt)
    return {
        "messages": [AIMessage(content=ai_message)],
        "available_activities": state["available_activities"],
        "waiting_for_selection": True 
    }