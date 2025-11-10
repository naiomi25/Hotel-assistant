# visto
from app.state.state import AgentState
from app.llm.llm import generate_response
from app.prompts.prompts import (
    no_selected_activities_prompt,
    no_available_activities_prompt,
)
from langchain_core.messages import AIMessage
from typing import Dict



def nodo_city(state: AgentState) -> Dict:
  
    
    selected = state.get("selected_activities", [])
    city_guide_url = "guia_turismo.pdf"
    
    # Caso 1: El huésped eligió ciudad desde el inicio (no seleccionó actividades)
    if not selected:
        print("(debug) El huésped eligió ir a la ciudad.")
        prompt = no_selected_activities_prompt(state)
        ai_message_content = generate_response(prompt)
        
    # Caso 2: Llegamos aquí desde "no hay disponibilidad"
    # (La disculpa ya se generó en process_human_response)
    else:
        ai_message_content = "📘 Aquí tienes la guía turística con las mejores actividades en la zona:"
    
    print("(debug) Nodo CITY ejecutado. Proporcionando guía.")
    
    return {
    **state,  
    "messages": state["messages"] + [AIMessage(content=ai_message_content)],
    "city_guide": f"http://127.0.0.1:5000/data_db/{city_guide_url}",
}