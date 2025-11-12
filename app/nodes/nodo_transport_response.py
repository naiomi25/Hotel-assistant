from app.state.state import AgentState
from app.prompts.prompts import ( response_ok_transport_prompt,response_refuse_transport_prompt,)     
from app.llm.llm import generate_response
from langchain_core.messages import AIMessage


def nodo_transport_response(state: AgentState) -> AgentState:
  

    # ⭐ OBTENER la respuesta del ÚLTIMO mensaje del usuario
    messages = state.get("messages", [])
    user_reply = ""

    # Buscar el último mensaje 
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            user_reply = msg.content
            break

    user_reply_clean = user_reply.lower().strip()
    print(f"🚗 (debug) Respuesta del huésped sobre transporte: '{user_reply_clean}'")

    #
    if any(
        word in user_reply_clean
        for word in [
            "sí",
            "si",
            "taxi",
            "guagua",
            "transporte",
            "bus",
            "autobús",
            "yes",
        ]
    ):
        print("✅ Usuario aceptó el transporte")
        prompt = response_ok_transport_prompt(state)
    else:
        print("❌ Usuario rechazó el transporte")
        prompt = response_refuse_transport_prompt(state)

    ai_message = generate_response(prompt)

    print("✅ Nodo TRANSPORTE_RESPUESTA completado")

    
    return {
        **state, 
        "messages": state["messages"] + [AIMessage(content=ai_message)],
        "waiting_for_transport": False,  
    }
