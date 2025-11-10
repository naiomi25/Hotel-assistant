from app.state.state import AgentState
from app.llm.llm import generate_response
from app.prompts.prompts import (
    selected_activities_prompt,
    no_available_activities_prompt,
)
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
        prompt = selected_activities_prompt(state)
    else:
        print("(debug) No hay disponibilidad. Generando mensaje de disculpa.")
        prompt = no_available_activities_prompt(state)

    # 1. Generar la respuesta del asistente basada en el resultado
    ai_message = generate_response(prompt)

    # 🧩 Debug adicional
    print(f"(debug) Mensaje generado: {ai_message[:120]}")
    print("(debug) Nodo process_human_response DEVUELVE:")
    print({
        "available_activities": available,
        "unavailable_activities": unavailable,
        "last_message": ai_message[:80],
    })

    return {
        "messages": state["messages"] + [AIMessage(content=ai_message)],
        "available_activities": available,
        "unavailable_activities": unavailable,
    }
