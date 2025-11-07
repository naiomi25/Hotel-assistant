from app.state.state import InitialState
from app.llm.llm import generate_response
from app.prompts.prompts import  no_selected_activities_prompt, no_available_activities_prompt


def nodo_city(state: InitialState) -> InitialState:
    
    selected = state.get("selected_activities", [])
    available = state.get("available_activities", [])
    
    state["city_guide"] = "app/data_db/guia_turismo.pdf"
    
    if not selected :
        print("(debug) El huésped no ha seleccionado actividades.")
        
        prompt = no_selected_activities_prompt(state)
        ai_message = generate_response(prompt)

    elif selected and not available:
        print("(debug) No hay actividades disponibles entre las seleccionadas por el huésped.")
        prompt = no_available_activities_prompt(state)
        ai_message = generate_response(prompt)
        
    else:
        print("(debug) Llegamos al nodo_city sin una causa esperada.")
        ai_message = "Aquí tienes una guía turística con las mejores actividades en la ciudad 😊"
        

    state["assistant_message"] = ai_message
    state.setdefault("messages", [])
    state["messages"].append({"role": "assistant", "content": ai_message})
    return state