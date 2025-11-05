from langgraph.graph import StateGraph, START, END
from state import initial_state
# from nodes.greeting import node_greeting


def build_graph():
    builder = StateGraph(dict)   
    # builder.add_node("greeting", node_greeting)
    # builder.add_node("weather", node_weather) 
    builder.add_edge(START, "greeting")
    builder.add_edge("greeting", END)
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
