# visto
from app.state.state import AgentState # Usamos AgentState
from app.prompts.prompts import offer_transport_prompt
from app.llm.llm import generate_response
from langchain_core.messages import AIMessage # CRÍTICO: Importar AIMessage

def nodo_transport_offer(state: AgentState) -> AgentState:
    prompt = offer_transport_prompt(state)
    ai_message = generate_response(prompt)

    print(f"(debug) Nodo OFRECER TRANSPORTE ejecutado")

    return {
        "messages": [AIMessage(content=ai_message)],
    }