from langgraph.graph import StateGraph, START, END
from app.state.state import initial_state
from app.nodes.nodo_guest_info import nodo_guest_info
from app.nodes.nodo_weather import nodo_weather


def build_graph():
    builder = StateGraph(dict)   
    builder.add_node("welcome", nodo_guest_info)
    builder.add_node("weather", nodo_weather) 
    builder.add_edge(START, "welcome")
    builder.add_edge("welcome", 'weather')
    graph = builder.compile()
    # generar PNG para visualizar
    graph.draw_mermaid_png("graph_stage_0.png")
    return graph

if __name__ == "__main__":
    graph = build_graph()
    # Ejemplo: invocar con estado simulado (como vendría del front)
    st = initial_state()
    st["room"] = "203"
    result = graph.invoke(st)
    print("Resultado del grafo (state):", result)
