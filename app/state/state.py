from typing import Annotated, List, Optional, TypedDict
from langchain_core.messages import BaseMessage 
import operator 

class UserInfo(TypedDict):
    name: str
    has_children: bool
    room: str

class AgentState(TypedDict):
    
    messages: Annotated[List[BaseMessage], operator.add]
    
    guest_info: UserInfo
    weather: str
    weather_description: str
    weather_filter: str
    selected_activities: List[str]
    available_activities: List[str]
    unavailable_activities: List[str]
    city_activities: List[str]
    final_choice: str
    city_guide: Optional[str]
    waiting_for_selection: bool 
    waiting_for_room: bool
    waiting_for_transport: bool  # ⭐ NUEVO ESTADO
    transport_response: Optional[str]  # ⭐ RESPUESTA DEL USUARIO SOBRE TRANSPORTE
    human_response: Optional[dict[str, str]]

def initial_state() -> AgentState:

    return {
        "guest_info": {
            "name": "",
            "has_children": False,
            "room": "",
        },
        'messages': [],
        "weather": "",
        "weather_description": "",
        "weather_filter": "",
        "selected_activities": [],
        "available_activities": [],
        "unavailable_activities": [],
        "city_activities": [],
        "final_choice": "",
        "city_guide": None,
        "waiting_for_selection": False,
        "waiting_for_room": False,
        "waiting_for_transport": False,  # ⭐ AÑADIR AL ESTADO INICIAL
        "transport_response": None,
    }