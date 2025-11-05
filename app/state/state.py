from typing import Dict, List, TypedDict

class UserInfo(TypedDict):
    name: str
    has_children: bool
    room: str


class InitialState(TypedDict):
    
    guest_info: UserInfo
    weather: str
    selected_activities: List[str]
    available_activities: List[str]
    unavailable_activities: List[str]
    city_activities: List[str]
    final_choice: str
