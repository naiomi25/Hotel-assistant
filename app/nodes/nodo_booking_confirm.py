# visto
from app.state.state import AgentState
from app.llm.llm import generate_response # Función mockeada para LLM
from app.prompts.prompts import selected_activities_prompt # Reusamos este prompt
from langchain_core.messages import AIMessage
from typing import Dict

def nodo_booking_confirm(state: AgentState) -> Dict:
    """
    Nodo final que genera el mensaje de confirmación de la reserva.
    Solo se ejecuta si el recepcionista ha confirmado al menos una actividad.
    """
    
    available = state.get("available_activities", [])
    
    # Esta variable se usa para generar un mensaje final limpio
    if available:
        final_choice = ", ".join(available)
        print(f"✅ Se han reservado las siguientes actividades: {final_choice}")
    else:
        # Aunque el grafo no debería llegar aquí si 'available' está vacío, 
        # es buena práctica asegurar que 'final_choice' exista.
        final_choice = ""
    
    # Usamos el prompt para que el LLM redacte el mensaje de confirmación
    prompt = selected_activities_prompt(state) 
    ai_message = generate_response(prompt)

    print("(debug) Nodo BOOKING CONFIRM ejecutado")
    
    # Devolvemos el mensaje del LLM y actualizamos la reserva final en el estado.
    return {
        "messages": [AIMessage(content=ai_message)],
        "final_choice": final_choice
    }