# visto
from app.state.state import AgentState # Usamos AgentState
from app.data_db.all_activities import all_activities

def nodo_select_activity(state: AgentState, user_selection: list[str] = None) -> AgentState:
    
   
    if not user_selection or (user_selection) == [None] or user_selection == []:
        print("(debug nodo select activity) El usuario no seleccionó actividades (irá a ciudad).")
        
        return {
            "selected_activities": [],
            "final_choice": ""
        }
    
    
    id_to_name = {a["id"]: a["name"] for a in all_activities}
    selected_names = [id_to_name[a] for a in user_selection if a in id_to_name]
    
    print(f"(debug nodo select activity) IDs seleccionadas: {user_selection}")
    print(f"(debug nodo select activity) Nombres seleccionados: {selected_names}")

    
    return {
        "selected_activities": selected_names,
        "waiting_for_selection": False 
    }