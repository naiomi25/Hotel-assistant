from flask import Blueprint, request, jsonify
from flask_cors import CORS
import uuid
import re
from app.graph import app_graph
from app.state.state import initial_state
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command  # ⭐ IMPORTANTE
import logging

api_bp = Blueprint("api", __name__, url_prefix="/api")
CORS(api_bp)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Funciones Auxiliares ---


def extract_room_number(text: str) -> str:
    """Extrae el número de habitación del mensaje del usuario."""
    match = re.search(r"\b\d{3,4}\b", text)
    return match.group() if match else None


def messages_to_json(messages):
    """Convierte objetos LangChain Messages en dicts simples."""
    serialized = []
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        serialized.append({"role": role, "content": content})
    return serialized


def _get_full_state(current_state, user_message=None):
    """Construye el estado completo para LangGraph."""
    base_state = {
        "guest_info": current_state.get("guest_info", initial_state()["guest_info"]),
        "weather": current_state.get("weather", ""),
        "weather_description": current_state.get("weather_description", ""),
        "weather_filter": current_state.get("weather_filter", ""),
        "selected_activities": current_state.get("selected_activities", []),
        "available_activities": current_state.get("available_activities", []),
        "unavailable_activities": current_state.get("unavailable_activities", []),
        "city_activities": current_state.get("city_activities", []),
        "final_choice": current_state.get("final_choice", ""),
        "city_guide": current_state.get("city_guide"),
        "waiting_for_selection": current_state.get("waiting_for_selection", False),
        "waiting_for_room": current_state.get("waiting_for_room", False),
        "waiting_for_transport": current_state.get(
            "waiting_for_transport", False   ), 
        "transport_response": current_state.get("transport_response"), 
        "human_response": current_state.get("human_response"),
        "session_id": current_state.get("session_id"),
    }

    current_messages = current_state.get("messages", [])
    if user_message:
        base_state["messages"] = current_messages + [HumanMessage(content=user_message)]
    else:
        base_state["messages"] = current_messages

    return base_state


# --- ENDPOINTS ---


@api_bp.route("/status/<session_id>", methods=["GET"])
def get_session_status(session_id):
    """Endpoint para que el frontend verifique si una sesión con interrupt terminó"""
    try:
        config = {"configurable": {"thread_id": session_id}}

        # Obtener estado actual del grafo
        state_snapshot = app_graph.get_state(config)

        # Verificar si hay interrupt pendiente
        has_interrupt = state_snapshot.next is not None and len(state_snapshot.next) > 0

        # Obtener el estado actual
        current_state = (
            state_snapshot.values if hasattr(state_snapshot, "values") else {}
        )

        if not has_interrupt:
            # No hay interrupt = el grafo terminó
            assistant_message = ""
            if current_state.get("messages"):
                last_message = current_state["messages"][-1]
                if hasattr(last_message, "content"):
                    assistant_message = last_message.content
                elif isinstance(last_message, dict) and "content" in last_message:
                    assistant_message = last_message["content"]

            # Convertir mensajes a formato JSON si es necesario
            if current_state.get("messages"):
                current_state["messages"] = messages_to_json(current_state["messages"])

            return jsonify(
                {
                    "status": "completed",
                    "has_interrupt": False,
                    "assistant_message": assistant_message,
                    "pdf_url": current_state.get("city_guide"),
                    "state": current_state,
                    "transport_info": current_state.get("transport_info"),
                }
            )
        else:
            # Todavía hay interrupt pendiente
            return jsonify(
                {
                    "status": "waiting",
                    "has_interrupt": True,
                    "next_nodes": (
                        list(state_snapshot.next) if state_snapshot.next else []
                    ),
                }
            )

    except Exception as e:
        logger.error(
            f"❌ Error obteniendo estado de sesión {session_id}: {e}", exc_info=True
        )
        return jsonify({"error": str(e)}), 500


@api_bp.route("/start_conversation", methods=["POST"])
def start_conversation():
    try:
        data = request.get_json()
        frontend_state = data.get("state", initial_state())
        user_message = data.get("user_message", "")

        session_id = frontend_state.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            frontend_state["session_id"] = session_id

        # ⭐ LEER SOLO CAMPOS ESPECÍFICOS DEL GRAFO (evitar conflictos)
        config = {"configurable": {"thread_id": session_id}}
        current_state = frontend_state.copy()  # Empezar con el estado del frontend

        try:
            graph_state_snapshot = app_graph.get_state(config)
            if (
                graph_state_snapshot
                and hasattr(graph_state_snapshot, "values")
                and graph_state_snapshot.values
            ):
                graph_values = graph_state_snapshot.values

                # ⭐ SOLO sincronizar campos específicos que necesitamos
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
            # current_state ya es frontend_state, no hacemos nada

        if "guest_info" not in current_state:
            current_state["guest_info"] = initial_state()["guest_info"]

        # ¿Esperando habitación?
        waiting_for_room = current_state.get("waiting_for_room", False)
        # ⭐ ¿Esperando respuesta de transporte?
        waiting_for_transport = current_state.get("waiting_for_transport", False)

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

        # ⭐ MANEJAR RESPUESTA DE TRANSPORTE
        elif waiting_for_transport:
            logger.info(f"🚗 Esperando respuesta de transporte: {user_message}")

            current_state["waiting_for_transport"] = False
            current_state["transport_response"] = (
                user_message  # ⭐ GUARDAR LA RESPUESTA EN EL ESTADO
            )

            # ⭐ SALTAR DIRECTAMENTE AL NODO transport_response
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

        # ⭐ DETECCIÓN DE @select_multiple
        if user_message.startswith("@select_multiple"):
            logger.info("🎯 Comando @select_multiple detectado")

            import json

            try:
                activities_json = user_message.replace("@select_multiple", "").strip()
                selected_activities = json.loads(activities_json)
                logger.info(f"📌 Actividades seleccionadas: {selected_activities}")

                current_state["selected_activities"] = selected_activities
                current_state["waiting_for_selection"] = False

                # ⭐ USAR COMMAND PARA SALTAR AL NODO select_activity
                full_state = _get_full_state(current_state)
                config = {"configurable": {"thread_id": session_id}}

                # ⭐ EJECUTAR CON INVOKE (forma correcta según documentación)
                result = app_graph.invoke(
                    Command(
                        update=full_state,
                        goto="select_activity",  # Saltar directamente a este nodo
                    ),
                    config=config,
                )

                # ⭐ DESPUÉS DE INVOKE, VERIFICAR SI HAY INTERRUPT
                state_after = app_graph.get_state(config)

                if state_after.next:  # Hay nodos pendientes = interrupt
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

                # Si no hay interrupt, procesar normalmente
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

        # Flujo NORMAL
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


@api_bp.route("/resume", methods=["POST"])
def resume_conversation():
    try:
        data = request.get_json()
        session_id = data.get("session_id")

        if not session_id:
            return jsonify({"error": "session_id es requerido"}), 400

        human_response = data.get("human_response", {})
        raw_available = data.get("available_activities", [])
        raw_unavailable = data.get("unavailable_activities", [])

        logger.info(f"🔄 Reanudando sesión {session_id}")
        logger.info(f"👂 human_response: {human_response}")

        # Normalizar disponibilidad
        available = []
        unavailable = []

        if isinstance(human_response, dict):
            for act, val in human_response.items():
                v = str(val).strip().lower()
                if v in {"sí", "si", "yes", "true", "1", "s", "y"}:
                    available.append(act)
                else:
                    unavailable.append(act)
        else:
            available = raw_available if isinstance(raw_available, list) else []
            unavailable = raw_unavailable if isinstance(raw_unavailable, list) else []

        logger.info(f"✅ Disponibles: {available}")
        logger.info(f"❌ No disponibles: {unavailable}")

        # ⭐ Reanudar interrupt con valor de respuesta humana
        resume_value = {
            "available_activities": available,
            "unavailable_activities": unavailable,
            "human_response": human_response,
        }

        logger.info(f"🔄 Reanudando interrupt con valor: {resume_value}")

        # Config de sesión
        config = {"configurable": {"thread_id": session_id}}

        from langgraph.types import Command

        try:
            # Verificar estado del grafo antes de resumir
            current_state = app_graph.get_state(config)
            logger.info(
                f"📊 Estado del grafo antes de resumir: {getattr(current_state, 'next', 'N/A')}"
            )

            # Reanudar correctamente con Command(resume=...)
            result = app_graph.invoke(Command(resume=resume_value), config=config)
            try:
                state_snapshot = app_graph.get_state(config)
                logger.info(f"🧠 DEBUG_STATE_NEXT: {getattr(state_snapshot, 'next', None)}")
                if hasattr(state_snapshot, "values"):
                    logger.info(f"🧠 DEBUG_STATE_VALUES_KEYS: {list(state_snapshot.values.keys())}")
                    if "messages" in state_snapshot.values:
                        logger.info(f"🧠 DEBUG_MESSAGES_LEN: {len(state_snapshot.values['messages'])}")
                        # Muestra los últimos 3 mensajes para ver el orden
                        for i, msg in enumerate(state_snapshot.values['messages'][-3:]):
                            logger.info(f"🧠 MSG[{i}] {msg}")
            except Exception as debug_e:
                logger.warning(f"⚠️ No se pudo obtener snapshot del estado: {debug_e}")

        except Exception as e:
            logger.error(f"❌ Error durante resume: {e}", exc_info=True)
            raise

        # Procesar resultado
        new_state = result if isinstance(result, dict) else {}
        new_state["session_id"] = session_id
        new_state["paused_at_node"] = None

        assistant_message = ""
        if new_state.get("messages"):
            last_message = new_state["messages"][-1]
            if isinstance(last_message, (AIMessage, SystemMessage)):
                assistant_message = last_message.content
            new_state["messages"] = messages_to_json(new_state["messages"])

        response_data = {
            "status": "resumed",
            "assistant_message": assistant_message,
            "pdf_url": new_state.get("city_guide"),
            "state": new_state,
        }
     
        logger.info("✅ Sesión reanudada correctamente")


        logger.info(f"📄 PDF URL generado: {new_state.get('city_guide')}")
        logger.info(f"💬 Mensaje final: {assistant_message[:100]}...")

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"❌ Error en resume: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

