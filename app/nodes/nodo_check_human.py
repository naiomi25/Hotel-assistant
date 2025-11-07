from app.state.state import InitialState


def nodo_check_human(state: InitialState) -> InitialState:
    
    selected = state.get("selected_activities", [])
    if not selected:
        print("(debug) No hay actividades seleccionadas.")
    
        return state

    available = []
    unavailable = []

    print("\n🔍 Comprobando disponibilidad...\n")

    for activity in selected:
        while True:
            respuesta = input(f"¿Hay disponibilidad para '{activity}'? (s/n): ").strip().lower()
            if respuesta == "s":
                available.append(activity)
                break
            elif respuesta == "n":
                unavailable.append(activity)
                break
            else:
                print("Respuesta no válida. Escribe 's' o 'n'.")

    state["available_activities"] = available
    state["unavailable_activities"] = unavailable
    
    if available:
        state["final_choice"] = ", ".join(available)
        print(f"\n✅ Se han reservado automáticamente las siguientes actividades: {state['final_choice']}")
        return state
    state["final_choice"] = ""

    print(f"\n✅ Disponibles: {available}")
    print(f"❌ No disponibles: {unavailable}")
    return state