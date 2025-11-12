# visto
from app.state.state import AgentState
from app.llm.llm import generate_response # Función mockeada para LLM
from app.prompts.prompts import selected_activities_prompt # Reusamos este prompt
from langchain_core.messages import AIMessage
from typing import Dict

def nodo_booking_confirm(state: AgentState) -> Dict:
    
    
    available = state.get("available_activities", [])
   
    if available:
        final_choice = ", ".join(available)
        print(f"✅ Se han reservado las siguientes actividades: {final_choice}")
    else:
        
        final_choice = ""
    
   
    prompt = selected_activities_prompt(state) 
    ai_message = generate_response(prompt)

    print("(debug) Nodo BOOKING CONFIRM ejecutado")
    
    return {
        "messages": [AIMessage(content=ai_message)],
        "final_choice": final_choice
    }