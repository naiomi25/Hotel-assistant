from typing import Dict, List, Optional, TypedDict

class UserInfo(TypedDict):
    name: str
    has_children: bool
    room: str

class Message(TypedDict):
    role: str
    content: str

class InitialState(TypedDict):
    
    guest_info: UserInfo
    assistant_message: Optional[str]
    messages: List[Message]
    weather: str
    weather_description: str
    weather_filter: str
    selected_activities: List[str]
    available_activities: List[str]
    unavailable_activities: List[str]
    city_activities: List[str]
    final_choice: str
    

def initial_state() -> InitialState:
   
    return {
        "guest_info": {
            "name": "",
            "has_children": False,
            "room": "",
        },
        'messages': [],
        "assistant_message": None,
        "weather": "",
        "weather_description": "",
        "weather_filter": "",
        "selected_activities": [],
        "available_activities": [],
        "unavailable_activities": [],
        "city_activities": [],
        "final_choice": "",
    }