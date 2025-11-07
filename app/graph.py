from langgraph.graph import StateGraph, START, END
from app.nodes.nodo_activities import nodo_activities
from app.nodes.nodo_antivities_outdoor import nodo_activities_outdoor
from app.nodes.nodo_check_human import nodo_check_human
from app.nodes.nodo_city import nodo_city
from app.nodes.nodo_select_activity import nodo_select_activity
from app.nodes.nodo_transport_offer import nodo_transport_offer
from app.nodes.nodo_transport_response import nodo_transport_response
from app.state.state import initial_state
from app.state.state import InitialState
from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather
from app.nodes.nodo_booking_confirm import nodo_booking_confirm


def  condicional_funcion_activities(state):
    return "outdoor" if state["weather_filter"] == "sol" else "indoor"

def condicional_user_city_or_hotel(state):
    return "city" if state['selected_activities'] == [] else "hotel"

def condicional_human_check(state):
    
    return "hotel" if state.get("available_activities") else "city"



def build_graph():
    
    builder = StateGraph(InitialState)

    # definimos los nodos
    
    builder.add_node("welcome", nodo_guest_info)
    builder.add_node("weather", nodo_weather) 
    builder.add_node('activities_indoor', nodo_activities)
    builder.add_node('activities_outdoor', nodo_activities_outdoor)
    builder.add_node('select_activity', nodo_select_activity)
    builder.add_node('human_check', nodo_check_human)
    builder.add_node('booking_confirm', nodo_booking_confirm)
    builder.add_node('city', nodo_city)
    builder.add_node('transport_offer', nodo_transport_offer)
    builder.add_node('transport_response', nodo_transport_response)

     # definimos las transiciones
    
    
    builder.add_edge(START, "welcome")
    builder.add_edge("welcome", 'weather')
    builder.add_conditional_edges(
        "weather",
        condicional_funcion_activities,
        {
            "outdoor": 'activities_outdoor',
            "indoor": 'activities_indoor',
        }
    )
    builder.add_edge("activities_outdoor", "select_activity")
    builder.add_edge("activities_indoor", "select_activity")
    builder.add_conditional_edges(
        "select_activity",
        condicional_user_city_or_hotel,
        {
            "city": 'city',
            "hotel": 'human_check',
        }
    )

    builder.add_conditional_edges(
        "human_check", 
        condicional_human_check,
        {
            "city": 'city',
            "hotel": 'booking_confirm',
        })
    builder.add_edge("city",'transport_offer')
    builder.add_edge("transport_offer", "transport_response")
    builder.add_edge("transport_response", END)
    builder.add_edge("booking_confirm", END)
    
    graph = builder.compile()
    
 
    # graph.get_graph().draw_png("hotel_graph.png")
    return graph