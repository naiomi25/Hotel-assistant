from app.llm.llm import generate_response
from app.prompts.prompts import selected_activities_prompt
from app.state.state import InitialState

def nodo_booking_confirm(state: InitialState) -> InitialState:
    
    selected = state.get("selected_activities", [])
    available = state.get("available_activities", [])
    
    if selected and available:
        prompt = selected_activities_prompt(state)
        ai_message = generate_response(prompt)

    state["assistant_message"] = ai_message
    state["messages"].append({
        "role": "assistant",
        "content": ai_message
    })

    print(f"(debug) Nodo CONFIRMAR RESERVA ejecutado")
    print(ai_message)

    return state
