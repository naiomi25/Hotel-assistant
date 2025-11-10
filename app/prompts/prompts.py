
from app.state.state import AgentState
# --- 1. Flujo de Bienvenida ---

def initial_welcome_prompt() -> str:
    """Solicita el número de habitación. (Se ejecuta antes de tener la info de huésped)."""
    return (
        "Tarea: Saluda amablemente al huésped y pide su número de habitación para "
        "darle una atención personalizada. Sé breve y cortés."
    )

def welcome_prompt(state: AgentState) -> str:
    """Bienvenida personalizada (se ejecuta después de obtener la info del huésped)."""
    guest_name = state["guest_info"]["name"]
    has_children = "Sí" if state["guest_info"]["has_children"] else "No"
    
    return f"""
Contexto: El huésped se llama **{guest_name}** y viaja con niños: {has_children}.
Tarea: Dale una bienvenida cálida y personalizada, mencionando su nombre y deseándole una feliz estancia.
"""

# --- 2. Flujo de Actividades ---

def activities_prompt_outdoor(state) -> str:
    """Ofrece actividades al aire libre."""
    activities = state.get('available_activities', [])
    
    return f"""
Contexto:
- Huésped: {state['guest_info']['name']}
- Viaja con niños: {'Sí' if state['guest_info']['has_children'] else 'No'}
- Clima: {state['weather_description']} ({state['weather']}°C). Es perfecto para planes al aire libre.

Tarea:
1.  Haz un comentario positivo sobre el buen clima.
2.  Muestra la lista de actividades al aire libre **exactamente como sigue**, numerada (1., 2., 3...).
3.  Pide al huésped que elija una o varias actividades de la lista.
Lista: {', '.join(activities)}
"""

def activities_prompt_indoor(state) -> str:
    """Ofrece actividades interiores."""
    activities = state.get('available_activities', [])
    
    return f"""
Contexto:
- Huésped: {state['guest_info']['name']}
- Viaja con niños: {'Sí' if state['guest_info']['has_children'] else 'No'}
- Clima: {state['weather_description']} ({state['weather']}°C). Sugiere planes interiores.

Tarea:
1.  Menciona amablemente el clima y sugiere que es el momento perfecto para disfrutar de la comodidad del hotel.
2.  Muestra la lista de actividades interiores **exactamente como sigue**, numerada (1., 2., 3...).
3.  Pide al huésped que elija una o varias actividades.
Lista: {', '.join(activities)}
"""

# --- 3. Flujo de Confirmación/Fallback (Tras Pausa Asíncrona) ---

def selected_activities_prompt(state) -> str:
    """Mensaje para confirmar la reserva de actividades (hay disponibilidad)."""
    confirmed = state['available_activities']
    
    return f"""
Contexto: El huésped {state['guest_info']['name']} viaja con niños: {'Sí' if state['guest_info']['has_children'] else 'No'}.
Actividades **reservadas y confirmadas**: {", ".join(confirmed)}

Tarea:
1.  Redacta un mensaje cálido confirmando la reserva.
2.  Menciona que estas actividades son excelentes elecciones.
3.  Si viaja con niños, añade un comentario amable para ellos.
4.  Recuérdale que Recepción está disponible para cualquier otra cosa.
5.  Despídete con una nota amable y de cortesía.
"""

def no_available_activities_prompt(state) -> str:
    """Mensaje cuando NO hay disponibilidad para las actividades solicitadas."""
    return f"""
Contexto: El huésped {state['guest_info']['name']} viaja con niños: {'Sí' if state['guest_info']['has_children'] else 'No'}.
Las actividades seleccionadas no tienen disponibilidad.

Tarea:
no saludes de nuevo al huésped.
1.  Disculpa brevemente la falta de disponibilidad.
2.  Menciona que, en su lugar, le vas a proporcionar la guía de la ciudad con actividades fuera del hotel (esto será la mejor alternativa).
3.  Si viaja con niños, añade un comentario amable.
"""

def no_selected_activities_prompt(state) -> str:
    """Mensaje cuando el huésped elige ir a la ciudad desde el inicio."""
    return f"""
Contexto: El huésped {state['guest_info']['name']} decidió no realizar actividades dentro del hotel.

Tarea:
1.  Agradece su respuesta con amabilidad.
2.  Indica que le vas a ofrecer una guía turística con planes fuera del hotel que puede descargar directamente.
3.  Usa un tono servicial y cercano.
"""

# --- 4. Flujo de Transporte ---

def offer_transport_prompt(state) -> str:
    """Oportunidad para ofrecer transporte a la ciudad."""
    return f"""
Contexto: El huésped {state['guest_info']['name']} acaba de recibir la guía turística.

Tarea:
no vuelvas a saludarla, Ofrécele reservar un transporte (taxi o guagua) desde el hotel con un tono servicial y amable. Pregúntale si le gustaría que se lo gestionemos.
"""

def response_ok_transport_prompt(state) -> str:
    """Mensaje cuando el huésped acepta el transporte."""
    return f"""
Contexto: El huésped {state['guest_info']['name']} aceptó la oferta de transporte.

Tarea:
1.  Confirma amablemente la reserva del transporte.
2.  Deséale un excelente día.
3.  Recuérdale que en recepción pueden atenderle para cualquier otro servicio.
"""

def response_refuse_transport_prompt(state) -> str:
    """Mensaje cuando el huésped rechaza el transporte."""
    return f"""
Contexto: El huésped {state['guest_info']['name']} prefirió no usar transporte.

Tarea:
1.  Agradécele con cortesía.
2.  Recuérdale que puede contactar recepción si cambia de idea o necesita algo.
"""