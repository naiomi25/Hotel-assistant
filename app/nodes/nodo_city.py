# visto
from app.state.state import AgentState
from app.llm.llm import generate_response
from app.prompts.prompts import (
    no_selected_activities_prompt,
    no_available_activities_prompt,
)
from langchain_core.messages import AIMessage
from typing import Dict


def nodo_city(state: AgentState) -> Dict:

    selected = state.get("selected_activities", [])
    available = state.get("available_activities", [])

    city_guide_url = "guia_turismo.pdf"

    if not selected:
        print("(debug) El huésped no ha seleccionado actividades.")

        prompt = no_selected_activities_prompt(state)

    elif selected and not available:
        print(
            "(debug) No hay actividades disponibles entre las seleccionadas por el huésped."
        )
        prompt = no_available_activities_prompt(state)

        # ⭐ GENERAR MENSAJE DE DISCULPA PRIMERO
        apology_message = generate_response(prompt)

        # ⭐ DESPUÉS AÑADIR EL PDF CON MENSAJE EXPLICATIVO
        pdf_message = "📘 Como alternativa, aquí tienes una guía turística con las mejores actividades disponibles en la zona:"

        return {
            "messages": [
                AIMessage(content=apology_message),
                AIMessage(content=pdf_message),
            ],
            "city_guide": f"http://127.0.0.1:5000/data_db/{city_guide_url}",  # ⭐ URL CORRECTA
        }

    else:
        print("(debug) Llegamos al nodo_city sin una causa esperada.")
        ai_message_content = (
            "Aquí tienes una guía turística con las mejores actividades en la ciudad 😊"
        )

        return {
            "messages": [AIMessage(content=ai_message_content)],
            "city_guide": f"http://127.0.0.1:5000/data_db/{city_guide_url}",  # ⭐ URL CORRECTA
        }

    # ⭐ ESTE BLOQUE YA NO SE EJECUTARÁ PORQUE CADA CASO RETORNA ARRIBA
    ai_message_content = generate_response(prompt)

    return {
        "messages": [AIMessage(content=ai_message_content)],
        "city_guide": f"http://127.0.0.1:5000/data_db/{city_guide_url}",  # ⭐ URL CORRECTA
    }
