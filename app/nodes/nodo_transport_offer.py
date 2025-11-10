from app.state.state import AgentState
from app.prompts.prompts import no_available_activities_prompt
from app.llm.llm import generate_response
from langchain_core.messages import AIMessage


def nodo_transport_offer(state: AgentState) -> AgentState:
    """
    Ofrece transporte al huésped y ESPERA su respuesta.
    Usa el mismo patrón que waiting_for_room.
    """

    prompt = no_available_activities_prompt(state)
    ai_message = generate_response(prompt)

    print(f"(debug) Nodo OFRECER TRANSPORTE ejecutado. Esperando respuesta...")

    return {
        **state,  # ⭐ PRESERVAR todo el estado existente (session_id, etc.)
        "messages": state["messages"] + [AIMessage(content=ai_message)],
        "waiting_for_transport": True,  # ⭐ CLAVE: Señal de espera
    }
