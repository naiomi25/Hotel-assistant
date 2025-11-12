# reanuda conveesacion interrumpida

from flask import Blueprint, request, jsonify
from app.graph import app_graph
from app.api.utils import messages_to_json
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command
import logging

logger = logging.getLogger(__name__)

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume", methods=["POST"])
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

        resume_value = {
            "available_activities": available,
            "unavailable_activities": unavailable,
            "human_response": human_response,
        }

        logger.info(f"🔄 Reanudando interrupt con valor: {resume_value}")

        config = {"configurable": {"thread_id": session_id}}

        try:
            # Verificar estado del grafo
            current_state = app_graph.get_state(config)
            logger.info(
                f"📊 Estado del grafo antes de resumir: {getattr(current_state, 'next', 'N/A')}"
            )

            result = app_graph.invoke(Command(resume=resume_value), config=config)
            try:
                state_snapshot = app_graph.get_state(config)
                logger.info(
                    f"🧠 DEBUG_STATE_NEXT: {getattr(state_snapshot, 'next', None)}"
                )
                if hasattr(state_snapshot, "values"):
                    logger.info(
                        f"🧠 DEBUG_STATE_VALUES_KEYS: {list(state_snapshot.values.keys())}"
                    )
                    if "messages" in state_snapshot.values:
                        logger.info(
                            f"🧠 DEBUG_MESSAGES_LEN: {len(state_snapshot.values['messages'])}"
                        )

                        for i, msg in enumerate(state_snapshot.values["messages"][-3:]):
                            logger.info(f"🧠 MSG[{i}] {msg}")
            except Exception as debug_e:
                logger.warning(f"⚠️ No se pudo obtener snapshot del estado: {debug_e}")

        except Exception as e:
            logger.error(f"❌ Error durante resume: {e}", exc_info=True)
            raise

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
