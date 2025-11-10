from langgraph.graph import StateGraph, START, END
from app.nodes.nodo_activities import nodo_activities
from app.nodes.nodo_antivities_outdoor import nodo_activities_outdoor
from app.nodes.nodo_check_human import nodo_check_human
from app.nodes.nodo_city import nodo_city
from app.nodes.nodo_transport_offer import nodo_transport_offer
from app.nodes.nodo_transport_response import nodo_transport_response
from app.nodes.nodo_process_human_response import nodo_process_human_response
from app.state.state import AgentState as InitialState
from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather
from app.nodes.nodo_booking_confirm import nodo_booking_confirm
from langgraph.checkpoint.memory import MemorySaver


memory_saver = MemorySaver()


# --- Funciones Condicionales ---
def condicional_is_guest_info_ready(state: InitialState) -> str:
    """Decide si continuar o esperar después del nodo de bienvenida."""
    waiting = state.get("waiting_for_room", False)
    guest_info = state.get("guest_info", {})
    room = guest_info.get("room", "").strip()

    print(f"🔍 [DEBUG] condicional_is_guest_info_ready:")
    print(f"   - waiting_for_room: {waiting}")
    print(f"   - guest_info.room: '{room}'")

    # PRIORIDAD 1: Si waiting_for_room es True, siempre esperar
    if waiting:
        print(f"   ➡️ Resultado: 'wait' (esperando habitación)")
        return "wait"

    # PRIORIDAD 2: Solo continuar si tenemos habitación Y no estamos esperando
    if room:  # Habitación válida y no vacía
        print(f"   ➡️ Resultado: 'ready' (habitación: {room})")
        return "ready"

    # Por defecto, esperar
    print(f"   ➡️ Resultado: 'wait' (no hay habitación)")
    return "wait"


def condicional_funcion_activities(state: InitialState) -> str:
    """Decide si sugerir actividades indoor o outdoor basado en el clima."""
    return "outdoor" if state["weather_filter"] == "sol" else "indoor"


def condicional_process_result(state: InitialState) -> str:
    """
    Decide la siguiente acción después de que el recepcionista ha respondido.
    Basado en si el nodo 'process_human_response' encontró disponibilidad.
    """
    available = state.get("available_activities", [])
    print(f"🔍 [DEBUG] condicional_process_result:")
    print(f"   - available_activities: {available}")
    
    if available:
        print(f"   ➡️ Resultado: 'confirm' (hay {len(available)} actividades disponibles)")
        return "confirm" 
    else:
        print(f"   ➡️ Resultado: 'city_fallback' (no hay actividades disponibles)")
        return "city_fallback"


# --- Construcción del Grafo ---


def build_graph():
    builder = StateGraph(InitialState)

    # Definimos los nodos
    builder.add_node("welcome", nodo_guest_info)
    builder.add_node("weather", nodo_weather)
    builder.add_node("activities_indoor", nodo_activities)
    builder.add_node("activities_outdoor", nodo_activities_outdoor)
    # 'select_activity' actúa como punto de transición forzado desde la API
    builder.add_node("select_activity", lambda state: state)
    builder.add_node("human_check", nodo_check_human)
    builder.add_node("process_human_response", nodo_process_human_response)
    builder.add_node("booking_confirm", nodo_booking_confirm)
    builder.add_node("city", nodo_city)
    builder.add_node("transport_offer", nodo_transport_offer)
    builder.add_node("transport_response", nodo_transport_response)

    # Definimos las transiciones

    # 1. Inicio y Bienvenida
    builder.add_edge(START, "welcome")
    # 2. Bienvenida -> Clima
    builder.add_conditional_edges(
        "welcome",
        condicional_is_guest_info_ready,
        {
            "ready": "weather",  # Si tenemos la info, continuamos
            "wait": END,  # Si NO la tenemos (es la primera ejecución), el grafo termina y espera el input del huésped.
        },
    )

    builder.add_conditional_edges(
        "weather",
        condicional_funcion_activities,
        {
            "outdoor": "activities_outdoor",
            "indoor": "activities_indoor",
        },
    )
    # 4. Actividades -> Esperar Selección del Huésped
    # Estos nodos terminan el flujo y el grafo espera un nuevo input con 'selected_activities'
    builder.add_edge("activities_outdoor", END)
    builder.add_edge("activities_indoor", END)

    # --- Flujo de la Pausa Asíncrona (se activa con config['next'] = 'select_activity') ---

    # 5. Desde el punto de control 'select_activity' -> Pausa Humana
    builder.add_edge("select_activity", "human_check")

    # 6. La transición de la PAUSA: 'human_check' (INTERRUPT) transiciona a 'process_human_response' al REANUDAR
    builder.add_edge("human_check", "process_human_response")

    # 7. Decisión después de procesar la respuesta humana
    builder.add_conditional_edges(
        "process_human_response",
        condicional_process_result,
        {
            "city_fallback": "city",  # Si NO hay disponibilidad
            "confirm": "booking_confirm",  # Si SÍ hay disponibilidad
        },
    )

    # 8. Rama de Confirmación
    builder.add_edge("booking_confirm", END)

    # 9. Rama de Ciudad (Fallback o Elección)
    builder.add_edge("city", "transport_offer")
    builder.add_edge("transport_offer", END)  # -> Espera respuesta de transporte

    # 10. Tras la respuesta de transporte, finaliza
    builder.add_edge("transport_response", END)

    graph = builder.compile(checkpointer=memory_saver)

    # ⚠️ NO se registran comandos, la API maneja la inyección de estado

    return graph


app_graph = build_graph()
