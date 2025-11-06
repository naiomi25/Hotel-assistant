
# Nodo 1 - Bienvenida
def wellcome_prompt(state):
    return f"¡Hola {state}, Bienvenido/a al Hotel Sol y Mar. Para poder sugerirte actividades personalizadas, ¿me puedes indicar tu número de habitación?"

# Nodo 3 - Actividades
def activities_prompt(state):
  
    return f"""
Eres un asistente de hotel amistoso y cercano.
Tienes esta información sobre el huésped:
- Nombre: {state['guest_info']['name']}
- Viaja con niños: {'Sí' if state['guest_info']['has_children'] else 'No'}
- Clima actual: {state['weather_description']}
- Temperatura: {state['weather']}°C
- Actividades disponibles: {', '.join(state['available_activities'])}

Redacta un mensaje natural y cordial invitando al huésped a elegir actividades.
Puedes improvisar frases sobre el clima y la situación, por ejemplo: 
“Veo que vienes sin niños y con este clima estupendo podrías probar estas actividades: …”
Pregunta cuál le gustaría elegir. Mantén el mensaje cercano y en primera persona.
"""