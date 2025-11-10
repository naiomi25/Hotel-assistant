from app.state.state import AgentState
from app.llm.llm import generate_response
from app.prompts.prompts import selected_activities_prompt, no_available_activities_prompt
from langchain_core.messages import AIMessage
from typing import Dict

def nodo_process_human_response(state: AgentState) -> Dict:
  
    
    available = state.get("available_activities", [])
    unavailable = state.get("unavailable_activities", [])
    
    print("\n🔍 Nodo PROCESAR RESPUESTA HUMANA ejecutado")
    print(f"✅ Disponibles (confirmadas por Recepción): {available}")
    print(f"❌ No disponibles: {unavailable}")

    # Si hay alguna actividad disponible, el flujo va a confirmación.
    if available:
        print("(debug) Hay disponibilidad. Generando mensaje de confirmación.")
        # Usamos el prompt de éxito/confirmación.
        prompt = selected_activities_prompt(state)
        
    # Si no hay ninguna disponible, el flujo va a la ciudad.
    else:
        print("(debug) No hay disponibilidad. Generando mensaje de disculpa y yendo a ciudad.")
        # Usamos el prompt de falta de disponibilidad.
        prompt = no_available_activities_prompt(state)

    # 1. Generar la respuesta del asistente basada en el resultado
    ai_message = generate_response(prompt)

 
    return {
        "messages": [AIMessage(content=ai_message)],
        "available_activities": available, 
        "unavailable_activities": unavailable,
    }