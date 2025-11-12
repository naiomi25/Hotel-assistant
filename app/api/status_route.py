"""
Ruta: GET /api/status/<session_id>
Obtiene el estado actual de una sesión
"""

from flask import Blueprint, jsonify
from app.graph import app_graph
from app.api.utils import messages_to_json
import logging

logger = logging.getLogger(__name__)

status_bp = Blueprint("status", __name__)


@status_bp.route("/status/<session_id>", methods=["GET"])
def get_session_status(session_id):
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
            assistant_message = ""
            if current_state.get("messages"):
                last_message = current_state["messages"][-1]
                if hasattr(last_message, "content"):
                    assistant_message = last_message.content
                elif isinstance(last_message, dict) and "content" in last_message:
                    assistant_message = last_message["content"]

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
