

# Inicia o continúa una conversación con el asistente


from flask import Blueprint, request, jsonify
from app.graph import app_graph
from app.state.state import initial_state
from app.api.utils import extract_room_number, messages_to_json, _get_full_state
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command
import uuid
import logging

logger = logging.getLogger(__name__)

start_conversation_bp = Blueprint("start_conversation", __name__)


@start_conversation_bp.route("/start_conversation", methods=["POST"])
def start_conversation():
    try:
        data = request.get_json()
        frontend_state = data.get("state", initial_state())
        user_message = data.get("user_message", "")

        session_id = frontend_state.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            frontend_state["session_id"] = session_id

        config = {"configurable": {"thread_id": session_id}}
        current_state = frontend_state.copy()

        try:
            graph_state_snapshot = app_graph.get_state(config)
            if (
                graph_state_snapshot
                and hasattr(graph_state_snapshot, "values")
                and graph_state_snapshot.values
            ):
                graph_values = graph_state_snapshot.values

                if "waiting_for_transport" in graph_values:
                    current_state["waiting_for_transport"] = graph_values[
                        "waiting_for_transport"
                    ]
                if "waiting_for_room" in graph_values:
                    current_state["waiting_for_room"] = graph_values["waiting_for_room"]

                logger.info(
                    f"📊 Estado sincronizado del grafo para sesión: {session_id}"
                )
                logger.info(
                    f"   - waiting_for_transport: {current_state.get('waiting_for_transport', False)}"
                )
            else:
                logger.info(f"🆕 Nuevo estado para sesión: {session_id}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo leer estado del grafo: {e}")

        if "guest_info" not in current_state:
            current_state["guest_info"] = initial_state()["guest_info"]

        waiting_for_room = current_state.get("waiting_for_room", False)
        waiting_for_transport = current_state.get("waiting_for_transport", False)

    #   habitación
        if waiting_for_room:
            logger.info("🔎 Esperando número de habitación...")
            room_number = extract_room_number(user_message)

            if room_number:
                logger.info(f"📋 Habitación detectada: {room_number}")
                current_state["guest_info"]["room"] = room_number
                current_state["waiting_for_room"] = False
            else:
                logger.info("⚠️ No se detectó habitación.")
                return jsonify(
                    {
                        "assistant_message": "Por favor, indícame tu número de habitación (ejemplo: 305 o 1204).",
                        "state": current_state,
                        "pdf_url": None,
                    }
                )

    #    transporte
        elif waiting_for_transport:
            logger.info(f"🚗 Esperando respuesta de transporte: {user_message}")

            current_state["waiting_for_transport"] = False
            current_state["transport_response"] = user_message

            full_state = _get_full_state(current_state, user_message)

            result = app_graph.invoke(
                Command(
                    update=full_state,
                    goto="transport_response",
                ),
                config={"configurable": {"thread_id": session_id}},
            )

            new_state = result if isinstance(result, dict) else current_state
            new_state["session_id"] = session_id

            assistant_message = ""
            if new_state.get("messages"):
                last_message = new_state["messages"][-1]
                if isinstance(last_message, (AIMessage, SystemMessage)):
                    assistant_message = last_message.content
                new_state["messages"] = messages_to_json(new_state["messages"])

            return jsonify(
                {
                    "status": "completed",
                    "assistant_message": assistant_message,
                    "state": new_state,
                }
            )

        # ---  @select_multiple ---
        if user_message.startswith("@select_multiple"):
            logger.info("🎯 Comando @select_multiple detectado")

            import json

            try:
                activities_json = user_message.replace("@select_multiple", "").strip()
                selected_activities = json.loads(activities_json)
                logger.info(f"📌 Actividades seleccionadas: {selected_activities}")

                current_state["selected_activities"] = selected_activities
                current_state["waiting_for_selection"] = False

                full_state = _get_full_state(current_state)
                config = {"configurable": {"thread_id": session_id}}

                result = app_graph.invoke(
                    Command(
                        update=full_state,
                        goto="select_activity",
                    ),
                    config=config,
                )

                state_after = app_graph.get_state(config)

                if state_after.next:
                    logger.info(
                        f"🛑 FRONTEND: Interrupt detectado - nodos pendientes: {state_after.next}"
                    )

                    return jsonify(
                        {
                            "status": "interrupted",
                            "assistant_message": f"Perfecto, voy a consultar la disponibilidad de: {', '.join(selected_activities)}. Un momento por favor...",
                            "state": current_state,
                            "session_id": session_id,
                        }
                    )
                else:
                    logger.info(
                        "✅ FRONTEND: No hay interrupt, grafo completado normalmente"
                    )

                new_state = result if isinstance(result, dict) else current_state
                new_state["session_id"] = session_id

                assistant_message = ""
                if new_state.get("messages"):
                    last_message = new_state["messages"][-1]
                    if isinstance(last_message, (AIMessage, SystemMessage)):
                        assistant_message = last_message.content
                    new_state["messages"] = messages_to_json(new_state["messages"])

                return jsonify(
                    {
                        "status": "completed",
                        "assistant_message": assistant_message,
                        "state": new_state,
                    }
                )

            except Exception as e:
                logger.error(f"Error procesando @select_multiple: {e}", exc_info=True)
                return jsonify({"error": f"Error: {str(e)}"}), 400

        # --- FLUJO NORMAL ---
        logger.info(f"🚀 Ejecutando grafo normal para sesión: {session_id}")

        full_state = _get_full_state(current_state, user_message)
        config = {"configurable": {"thread_id": session_id}}

        result = app_graph.invoke(full_state, config=config)

        new_state = result if isinstance(result, dict) else current_state
        new_state["session_id"] = session_id

        assistant_message = ""
        if new_state.get("messages"):
            last_message = new_state["messages"][-1]
            if isinstance(last_message, (AIMessage, SystemMessage)):
                assistant_message = last_message.content
            new_state["messages"] = messages_to_json(new_state["messages"])

        response_data = {
            "status": "completed",
            "assistant_message": assistant_message,
            "pdf_url": new_state.get("city_guide"),
            "state": new_state,
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"❌ Error en start_conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
