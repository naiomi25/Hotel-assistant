from app.state.state import AgentState
from langgraph.types import interrupt

def nodo_check_human(state: AgentState):
    """
    Nodo que pausa el flujo con interrupt() para validación humana.
    Este es el VERDADERO human-in-the-loop pattern de LangGraph.
    """
    selected = state.get("selected_activities", [])

    if not selected:
        print("(debug) No hay actividades seleccionadas, omitiendo chequeo humano.")
        return state

    print(f"🛑 [INTERRUPT] Pausando grafo para validación humana de: {selected}")
    
    
    # El grafo se PAUSA aquí hasta que se reanude con Command(resume=...)
    # value = interrupt({
    #     "question": "¿Hay disponibilidad para las actividades seleccionadas?",
    #     "selected_activities": selected,
    #     "awaiting_confirmation": True
    # })
    updated = interrupt({
        "question": "¿Hay disponibilidad para las actividades seleccionadas?",
        "selected_activities": selected,
    })
    
    # Cuando se reanude, 'value' contendrá la respuesta del humano
    print(f"✅ [RESUME] Interrupt reanudado con respuesta: {updated}")
    
    # Devolver el estado actualizado con la respuesta
    return {
        "available_activities": updated.get("available_activities", []),
        "unavailable_activities": updated.get("unavailable_activities", []),
        "human_response": updated.get("human_response"),
    }