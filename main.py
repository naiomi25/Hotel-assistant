

if __name__ == "__main__":
    
    graph = build_graph()
    # Ejemplo: invocar con estado simulado (como vendría del front)
    state = initial_state()
    state["guest_info"]["room"] = "103"
    state = nodo_transport_offer(state)
    
    # Simulamos respuesta del huésped
    respuesta_usuario = input("Cliente: ")
    result = nodo_transport_response(state, respuesta_usuario)
    print(result["assistant_message"])
   
    result = graph.invoke(state)
    print("Resultado del grafo (state):", result)

