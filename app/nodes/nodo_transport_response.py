from app.state.state import InitialState
from app.prompts.prompts import response_ok_transport_prompt, response_refuse_transport_prompt
from app.llm.llm import generate_response


def nodo_transport_response(state: InitialState, user_reply: str = "") -> InitialState:
    user_reply = user_reply.lower().strip()
    print(f"(debug) Respuesta del huésped: {user_reply}")

    if any(word in user_reply for word in ["sí", "si", "taxi", "guagua", "transporte", "bus", "autobús"]):
       prompt  = response_ok_transport_prompt(state)
    else:
       prompt = response_refuse_transport_prompt(state)

    ai_message = generate_response(prompt)
    state["assistant_message"] = ai_message
    state["messages"].append({
        "role": "assistant",
        "content": ai_message
    })
    print("(debug) Nodo TRANSPORTE_RESPUESTA ejecutado")
    return state