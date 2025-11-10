
# from langgraph.graph import StateGraph, START, END
# from app.nodes.nodo_activities import nodo_activities
# from app.nodes.nodo_antivities_outdoor import nodo_activities_outdoor
# from app.state.state import initial_state
# from app.nodes.nodo_guest_info import nodo_guest_info
# from app.nodes.nodo_weather import nodo_weather
# from app.nodes.nodo_transport_offer import nodo_transport_offer
# from app.nodes.nodo_transport_response import nodo_transport_response

# def  condicional_funcion_activities(state):
#     return state["weather_filter"]

# def build_graph():
#     builder = StateGraph(dict)

#     # definimos los nodos
    
#     builder.add_node("welcome", nodo_guest_info)
#     builder.add_node("weather", nodo_weather) 
#     builder.add_node('activities_indoor', nodo_activities)
#     builder.add_node('activities_outdoor', nodo_activities_outdoor)
    
    
#      # definimos las transiciones
    
    
#     builder.add_edge(START, "welcome")
#     builder.add_edge("welcome", 'weather')
#     builder.add_conditional_edges(
#         "weather",
#         condicional_funcion_activities,
#         {
#             "outdoor": 'activities_outdoor',
#             "indoor": 'activities_indoor',
#         }
#     )
    
#     graph = builder.compile()
    
#     # # generar PNG para visualizar
#     # graph.draw_mermaid_png("graph_stage_0.png")
#     return graph

# if __name__ == "__main__":
    
#     graph = build_graph()
#     # Ejemplo: invocar con estado simulado (como vendría del front)
#     state = initial_state()
#     state["guest_info"]["room"] = "103"
#     state = nodo_transport_offer(state)
    
#     # Simulamos respuesta del huésped
#     respuesta_usuario = input("Cliente: ")
#     result = nodo_transport_response(state, respuesta_usuario)
#     print(result["assistant_message"])
   
#     result = graph.invoke(state)
#     print("Resultado del grafo (state):", result)

