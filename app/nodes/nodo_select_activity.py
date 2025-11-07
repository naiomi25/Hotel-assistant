from app.state.state import InitialState
from app.data_db.all_activities import all_activities

def nodo_select_activity(state: InitialState, user_selection: list[str] = None) -> InitialState:
    
    # Si el usuario no seleccionó nada:
    # if not user_selection or (user_selection) == [None]:
    #     state["selected_activities"] = []
    #     state["final_choice"] = ""
    #     print("(debug nodo select activity) El usuario no seleccionó actividades.")
    #     return state
    
    
    if user_selection is None:
        # Simulación temporal
        user_selection = ["A1", "A2"]  # ← AQUÍ SE SIMULA

    # Mapear IDs seleccionadas a nombres
    id_to_name = {a["id"]: a["name"] for a in all_activities}
    selected_names = [id_to_name[a] for a in user_selection if a in id_to_name]
    
    state["selected_activities"] = selected_names

    print(f"(debug nodo select activity) IDs seleccionadas: {user_selection}")
    print(f"(debug nodo select activity) Nombres seleccionados: {state['selected_activities']}")

    return state