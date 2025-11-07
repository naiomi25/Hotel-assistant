from app.state.state import InitialState
from app.prompts.prompts import offer_transport_prompt
from app.llm.llm import generate_response
# from langgraph.prebuilt import interrupt

def nodo_transport_offer(state: InitialState) -> InitialState:
    prompt = offer_transport_prompt(state)
    ai_message = generate_response(prompt)

    state["assistant_message"] = ai_message
    state["messages"].append({
        "role": "assistant",
        "content": ai_message
    })

    print(f"(debug) Nodo OFRECER TRANSPORTE ejecutado")
    print(ai_message)
    # interrupt("Esperando respuesta del huésped (sí/no/taxi/guagua)...")

    return state