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

    if waiting:
        print(f"   ➡️ Resultado: 'wait' (esperando habitación)")
        return "wait"

    if room: 
        print(f"   ➡️ Resultado: 'ready' (habitación: {room})")
        return "ready"

    print(f"   ➡️ Resultado: 'wait' (no hay habitación)")
    return "wait"


def condicional_funcion_activities(state: InitialState) -> str:
    return "outdoor" if state["weather_filter"] == "sol" else "indoor"


def condicional_transport_ready(state: InitialState) -> str:
   
    waiting = state.get("waiting_for_transport", False)


    if waiting:
        print(f"   ➡️ Resultado: 'wait' (esperando respuesta transporte)")
        return "wait"

    print(f"   ➡️ Resultado: 'ready' (respuesta recibida)")
    return "ready"


def condicional_process_result(state: InitialState) -> str:
   
    available = state.get("available_activities", [])
    print(f"🔍 [DEBUG] condicional_process_result:")
    
    if available:
        print(f"   ➡️ Resultado: 'confirm' (hay {len(available)} actividades disponibles)")
        return "confirm" 
    else:
        print(f"   ➡️ Resultado: 'city_fallback' (no hay actividades disponibles)")
        return "city_fallback"


# --- Construcción del Grafo ---


def build_graph():
    builder = StateGraph(InitialState)

    builder.add_node("welcome", nodo_guest_info)
    builder.add_node("weather", nodo_weather)
    builder.add_node("activities_indoor", nodo_activities)
    builder.add_node("activities_outdoor", nodo_activities_outdoor)
    builder.add_node("select_activity", lambda state: state)
    builder.add_node("human_check", nodo_check_human)
    builder.add_node("process_human_response", nodo_process_human_response)
    builder.add_node("booking_confirm", nodo_booking_confirm)
    builder.add_node("city", nodo_city)
    builder.add_node("city_delay", lambda state: state)
    builder.add_node("transport_offer", nodo_transport_offer)
    builder.add_node("transport_response", nodo_transport_response)
    builder.add_node("await_transport_response", lambda state: state)

   

    
    builder.add_edge(START, "welcome")
    builder.add_conditional_edges(
        "welcome",
        condicional_is_guest_info_ready,
        {
            "ready": "weather",  
            "wait": END,  
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
    builder.add_edge("activities_outdoor", END)
    builder.add_edge("activities_indoor", END)
    builder.add_edge("select_activity", "human_check")
    builder.add_edge("human_check", "process_human_response")
    builder.add_conditional_edges(
        "process_human_response",
        condicional_process_result,
        {
            "city_fallback": "city_delay",  
            "confirm": "booking_confirm", 
        },
    )
    builder.add_edge("city_delay", "city")
    builder.add_edge("booking_confirm", END)
    builder.add_edge("city", "transport_offer")
    builder.add_conditional_edges(
        "transport_offer",
        condicional_transport_ready,
        {
            "ready": "transport_response", 
            "wait": END,  
        },
    )
    builder.add_edge("transport_response", END)
    graph = builder.compile(checkpointer=memory_saver)

  
    return graph


app_graph = build_graph()
