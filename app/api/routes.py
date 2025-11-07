from flask import Blueprint, request, jsonify, current_app, send_file
from app.config import settings
from app.nodes.nodo_transport_offer import nodo_transport_offer
from app.nodes.nodo_booking_confirm import nodo_booking_confirm
from app.nodes.nodo_city import nodo_city
from app.nodes.nodo_activities import nodo_activities
from app.nodes.nodo_antivities_outdoor import nodo_activities_outdoor

from app.nodes.nodo_weather import nodo_weather
from app.state.state import initial_state
from app.state.state import InitialState
from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_check_human import nodo_check_human
from app.nodes.nodo_transport_response import nodo_transport_response

import json
import os

api_bp = Blueprint("api", __name__)

@api_bp.route("/start_conversation", methods=["POST"])
def start_conversation():
  
    data = request.get_json() or {}
    
# recupero el estado o inicio uno nuevo

    state: InitialState = data.get("state") or initial_state()
    user_message = data.get("user_message", "").strip()
    
 # Guardar número de habitación
    if user_message and user_message.isdigit():
        state["guest_info"]["room"] = user_message
        
# registro
    state.setdefault("messages", [])
    state["messages"].append({"role": "user", "content": user_message})
    
# 1 nodo
    state = nodo_guest_info(state)
    
# ¿tenemos ya habitación?
    if state["guest_info"]["room"]:
        state = nodo_weather(state)
        if state["weather_filter"] == "lluvia":
            state = nodo_activities(state)  # actividades indoor
        else:
            state = nodo_activities_outdoor(state)  # actividades outdoor
            
# Si el usuario selecciona actividades, verificamos su disponibilidad
    if user_message.startswith("@select_multiple"):
        payload = user_message.replace("@select_multiple", "").strip()
        try:
            selected = json.loads(payload)
        except Exception:
            selected = [s.strip() for s in payload.split(",") if s.strip()]

        # Guardamos las actividades seleccionadas
        state.setdefault("selected_activities", [])
        for act in selected:
            if act not in state["selected_activities"]:
                state["selected_activities"].append(act)

        state["waiting_for_selection"] = False

        # Mensaje inicial
        state["assistant_message"] = (
            f"Perfecto — has seleccionado: {', '.join(state['selected_activities'])}."
        )
        state.setdefault("messages", []).append(
            {"role": "assistant", "content": state["assistant_message"]}
        )

        # Validación del recepcionista
        state = nodo_check_human(state)
        pdf_url = None  # Seguridad

        # ✅ Si hay disponibilidad → confirmar y limpiar
        if state.get("available_activities"):
            state = nodo_booking_confirm(state)
            state["available_activities"] = []  # Limpieza visual
            return jsonify({
                "assistant_message": state["assistant_message"],
                "state": state
            })

        # 🚫 Si NO hay disponibles → primero la guía, luego transporte
        else:
            state = nodo_city(state)

            # Mostramos primero el mensaje de la guía
            guide_message = state["assistant_message"]
            pdf_url = None

            if state.get("city_guide"):
                pdf_filename = state["city_guide"]
                pdf_url = f"http://127.0.0.1:5000/api/download/{pdf_filename}"

            # Limpiamos actividades
            state["available_activities"] = []

            # Devolvemos la guía antes del transporte
            response = {
                "assistant_message": guide_message,
                "pdf_url": pdf_url,
                "state": state
            }

            # 🚕 A continuación (en segundo mensaje), Nayra ofrecerá transporte
            state = nodo_transport_offer(state)
            state["next_message"] = state["assistant_message"]

            # Agregamos esta bandera para que el front sepa que hay un mensaje pendiente
            response["next_message"] = state["next_message"]

            return jsonify(response)

    # Usuario indica que no le interesa ninguna actividad
    if user_message.startswith("@none"):
        state["selected_activities"] = []
        state["waiting_for_selection"] = False

        # Mensaje inicial
        state["assistant_message"] = (
            "Entendido. No te preocupes — podemos proponerte otras opciones más tarde."
        )
        state.setdefault("messages", []).append(
            {"role": "assistant", "content": state["assistant_message"]}
        )

        # Pasamos al nodo de guía turística
        state = nodo_city(state)
        pdf_url = None

        # Guardamos mensaje de la guía
        guide_message = state["assistant_message"]

        if state.get("city_guide"):
            pdf_filename = state["city_guide"]
            pdf_url = f"http://127.0.0.1:5000/api/download/{pdf_filename}"

        # 🧹 Limpiamos actividades (para que desaparezcan los botones)
        state["available_activities"] = []

        # Devolvemos primero el mensaje de la guía y el PDF
        response = {
            "assistant_message": guide_message,
            "pdf_url": pdf_url,
            "state": state
        }

        # 🚕 A continuación, Nayra ofrecerá el transporte
        state = nodo_transport_offer(state)
        state["next_message"] = state["assistant_message"]

        # Agregamos esta bandera para que el front sepa que hay un mensaje pendiente
        response["next_message"] = state["next_message"]

        return jsonify(response)


# 🚕 Si el huésped responde al transporte (ESTO SE MANTIENE ✅)
   # 🚕 Si el huésped responde al transporte (aunque no mencione "taxi" explícitamente)
    if any(word in user_message.lower() for word in ["taxi", "guagua", "transporte", "sí", "no", "vale", "claro", "gracias", "ok", "por favor", "mejor no"]):

    # 🧭 Detectar intención de transporte según palabras clave
        positive = any(word in user_message.lower() for word in ["sí", "claro", "por favor", "ok", "vale"])
        negative = any(word in user_message.lower() for word in ["no", "gracias", "mejor no"])

        if positive:
            state["transport_choice"] = "yes"
            state = nodo_transport_response(state, accepted=True)

        elif negative:
            state["transport_choice"] = "no"
            state = nodo_transport_response(state, accepted=False)

        else:
            # si menciona transporte sin especificar sí/no
            state["assistant_message"] = "¿Podrías confirmarme si deseas que te reserve el transporte?"

        # 🚦 Aquí cerramos el flujo con el mensaje final
        return jsonify({
            "assistant_message": state["assistant_message"],
            "state": state
        })


    return jsonify({
    "assistant_message": state.get("assistant_message", "No entendí tu mensaje, ¿podrías repetirlo?"),
    "state": state
})
@api_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    # 🔍 Obtener la ruta absoluta al directorio raíz del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # → app/
    pdf_path = os.path.join(base_dir, "data_db", filename)
    print(f"(debug) Ruta ABSOLUTA del PDF: {pdf_path}")

    # 🔒 Comprobar si el archivo existe
    if not os.path.exists(pdf_path):
        return jsonify({"error": f"Archivo no encontrado: {pdf_path}"}), 404

    # 📦 Enviar el archivo al cliente
    return send_file(pdf_path)
    

      
           