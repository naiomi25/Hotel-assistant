# visto
from app.state.state import AgentState # Usamos AgentState
from app.prompts.prompts import response_ok_transport_prompt, response_refuse_transport_prompt
from app.llm.llm import generate_response
from langchain_core.messages import AIMessage, HumanMessage # CRÍTICO: Importar mensajes

def nodo_transport_response(state: AgentState) -> AgentState:
    
    # ⭐ OBTENER LA RESPUESTA DEL ESTADO
    user_reply = state.get("transport_response", "")
    user_message = HumanMessage(content=user_reply)
    
    user_reply_clean = user_reply.lower().strip()
    print(f"(debug) Respuesta del huésped sobre transporte: {user_reply_clean}")

    if any(word in user_reply_clean for word in ["sí", "si", "taxi", "guagua", "transporte", "bus", "autobús"]):
        prompt = response_ok_transport_prompt(state)
    else:
        prompt = response_refuse_transport_prompt(state)

    ai_message = generate_response(prompt)
    
    print("(debug) Nodo TRANSPORTE_RESPUESTA ejecutado")
    
    # CRÍTICO: Devolver AMBOS mensajes (el del usuario y el del asistente)
    return {
        "messages": [user_message, AIMessage(content=ai_message)],
    }