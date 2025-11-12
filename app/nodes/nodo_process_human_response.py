from app.state.state import AgentState
from app.llm.llm import generate_response
from app.prompts.prompts import (selected_activities_prompt, no_available_activities_prompt,)
from langchain_core.messages import AIMessage
from typing import Dict


def nodo_process_human_response(state: AgentState) -> Dict:
    available = state.get("available_activities", [])
    unavailable = state.get("unavailable_activities", [])

    if available:
        print("(debug) Hay disponibilidad. Generando mensaje de confirmación.")
        prompt = selected_activities_prompt(state)
    else:
        print("(debug) No hay disponibilidad. Generando mensaje de disculpa.")
        prompt = no_available_activities_prompt(state)

    
    ai_message = generate_response(prompt)

    # 🧩 Debug adicional
    print(f"(debug) Mensaje generado: {ai_message[:120]}")
    
    return {
        "messages": state["messages"] + [AIMessage(content=ai_message)],
        "available_activities": available,
        "unavailable_activities": unavailable,
    }
