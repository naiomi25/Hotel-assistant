# Estructura Modular del Backend API

## 📁 Organización de Archivos

```
app/api/
├── routes.py                      # Archivo principal (refactorizado)
├── utils.py                       # Funciones auxiliares compartidas
├── status_route.py               # Ruta GET /status/<session_id>
├── start_conversation_route.py   # Ruta POST /start_conversation
└── resume_route.py               # Ruta POST /resume
```

## 🎯 Descripción de Módulos

### **routes.py** - Archivo Principal

Archivo principal simplificado que registra todos los blueprints modulares. Reducido de **445 líneas** a solo **~25 líneas**.

**Responsabilidades:**

- Crear el blueprint principal `api_bp`
- Configurar CORS
- Registrar todos los blueprints modulares
- Configurar logging

**Código:**

```python
api_bp = Blueprint("api", __name__, url_prefix="/api")
CORS(api_bp)

api_bp.register_blueprint(status_bp)
api_bp.register_blueprint(start_conversation_bp)
api_bp.register_blueprint(resume_bp)
```

---

### **utils.py** - Utilidades Compartidas

Funciones auxiliares utilizadas por múltiples rutas.

**Funciones:**

#### `extract_room_number(text: str) -> str`

Extrae el número de habitación del mensaje del usuario usando regex.

- **Patrón**: `\b\d{3,4}\b` (3-4 dígitos)
- **Uso**: Validar y extraer número de habitación del usuario

#### `messages_to_json(messages) -> list`

Convierte objetos LangChain Messages a diccionarios JSON simples.

- **Input**: Lista de objetos Message (HumanMessage, AIMessage, etc.)
- **Output**: Lista de dicts con `role` y `content`
- **Uso**: Serializar mensajes para enviar al frontend

#### `_get_full_state(current_state, user_message=None) -> dict`

Construye el estado completo para LangGraph preservando todos los campos.

- **Input**: Estado actual y mensaje opcional del usuario
- **Output**: Estado completo con todos los campos requeridos
- **Uso**: Preparar estado antes de invocar el grafo

---

### **status_route.py** - Ruta de Estado

**Endpoint**: `GET /api/status/<session_id>`

**Propósito**: Obtener el estado actual de una sesión durante el polling.

**Funcionalidad:**

1. Obtiene el snapshot del estado usando `app_graph.get_state(config)`
2. Verifica si hay interrupciones pendientes (`state_snapshot.next`)
3. Retorna diferentes respuestas según el estado:
   - **"completed"**: Sesión completada, incluye mensajes y PDF
   - **"waiting"**: Hay interrupciones pendientes

**Respuesta (completed):**

```json
{
  "status": "completed",
  "has_interrupt": false,
  "assistant_message": "...",
  "pdf_url": "...",
  "state": {...},
  "transport_info": {...}
}
```

**Respuesta (waiting):**

```json
{
  "status": "waiting",
  "has_interrupt": true,
  "next_nodes": ["node_name"]
}
```

---

### **start_conversation_route.py** - Ruta Principal

**Endpoint**: `POST /api/start_conversation`

**Propósito**: Iniciar una nueva conversación o continuar una existente.

**Funcionalidad:**

1. **Generación de session_id**: Crea UUID si no existe
2. **Sincronización de estado**: Lee estado del grafo si existe
3. **Manejo de waiting_for_room**: Detecta y procesa número de habitación
4. **Manejo de waiting_for_transport**: Procesa respuesta de transporte
5. **Comando @select_multiple**: Maneja selección de múltiples actividades
6. **Flujo normal**: Invoca el grafo con el estado completo

**Flujos de Ejecución:**

#### 1. Flujo de Habitación

```python
if waiting_for_room:
    room_number = extract_room_number(user_message)
    if room_number:
        # Actualizar estado y continuar
    else:
        # Solicitar número de habitación de nuevo
```

#### 2. Flujo de Transporte

```python
elif waiting_for_transport:
    current_state["transport_response"] = user_message
    result = app_graph.invoke(
        Command(update=full_state, goto="transport_response"),
        config=config
    )
```

#### 3. Flujo de Selección de Actividades

```python
if user_message.startswith("@select_multiple"):
    selected_activities = json.loads(activities_json)
    result = app_graph.invoke(
        Command(update=full_state, goto="select_activity"),
        config=config
    )
    # Detectar si hay interrupt
    if state_after.next:
        return {"status": "interrupted", ...}
```

#### 4. Flujo Normal

```python
result = app_graph.invoke(full_state, config=config)
```

**Respuesta:**

```json
{
  "status": "completed" | "interrupted",
  "assistant_message": "...",
  "pdf_url": "...",
  "state": {...},
  "session_id": "uuid"
}
```

---

### **resume_route.py** - Ruta de Reanudación

**Endpoint**: `POST /api/resume`

**Propósito**: Reanudar una conversación interrumpida (human-in-the-loop).

**Funcionalidad:**

1. **Validación**: Verifica que existe `session_id`
2. **Normalización de respuestas**: Procesa `human_response` y clasifica actividades en disponibles/no disponibles
3. **Resume del grafo**: Usa `Command(resume=resume_value)` para continuar
4. **Debug logging**: Registra estado antes y después de resumir

**Normalización de Respuestas:**

```python
if isinstance(human_response, dict):
    for act, val in human_response.items():
        v = str(val).strip().lower()
        if v in {"sí", "si", "yes", "true", "1", "s", "y"}:
            available.append(act)
        else:
            unavailable.append(act)
```

**Resume del Grafo:**

```python
resume_value = {
    "available_activities": available,
    "unavailable_activities": unavailable,
    "human_response": human_response,
}

result = app_graph.invoke(Command(resume=resume_value), config=config)
```

**Respuesta:**

```json
{
  "status": "resumed",
  "assistant_message": "...",
  "pdf_url": "...",
  "state": {...}
}
```

---

## 🔄 Flujo de Datos

```
Flask App
  └─> routes.py (api_bp)
        ├─> status_bp (/status/<session_id>)
        │     └─> app_graph.get_state()
        │
        ├─> start_conversation_bp (/start_conversation)
        │     ├─> Validar waiting_for_room
        │     ├─> Validar waiting_for_transport
        │     ├─> Procesar @select_multiple
        │     └─> app_graph.invoke()
        │
        └─> resume_bp (/resume)
              ├─> Normalizar human_response
              └─> app_graph.invoke(Command(resume=...))
```

---

## 📊 Integración con LangGraph

### Estados Manejados:

- `waiting_for_room`: Esperando número de habitación
- `waiting_for_transport`: Esperando respuesta de transporte (sí/no)
- `waiting_for_selection`: Esperando selección de actividades
- `human_response`: Respuesta del recepcionista (interrupt)

### Comandos LangGraph:

```python
# Continuar desde un nodo específico
Command(update=state, goto="node_name")

# Reanudar después de un interrupt
Command(resume=resume_value)
```

### Config de Thread:

```python
config = {"configurable": {"thread_id": session_id}}
```

---

## ✅ Beneficios de la Modularización

1. **Separación de responsabilidades**: Cada archivo tiene una función clara
2. **Mantenibilidad**: Más fácil encontrar y modificar código
3. **Testing**: Cada ruta se puede testear independientemente
4. **Legibilidad**: Código más organizado y documentado
5. **Escalabilidad**: Fácil agregar nuevas rutas

---

## 🚀 Sin Cambios en la Funcionalidad

Toda la funcionalidad original se mantiene intacta:

- ✅ Gestión de sesiones con UUID
- ✅ Manejo de waiting_for_room
- ✅ Manejo de waiting_for_transport
- ✅ Comando @select_multiple
- ✅ Interrupciones (human-in-the-loop)
- ✅ Polling de estado
- ✅ Serialización de mensajes
- ✅ Integración con LangGraph

La refactorización es **puramente estructural**, sin cambios en el comportamiento.

---

## 📝 Logging

Todos los módulos usan el mismo sistema de logging:

```python
import logging
logger = logging.getLogger(__name__)
```

**Niveles utilizados:**

- `logger.info()`: Flujo normal de operaciones
- `logger.warning()`: Advertencias no críticas
- `logger.error()`: Errores con stack trace

**Ejemplos de logs:**

- `📊 Estado sincronizado del grafo para sesión: {session_id}`
- `🔎 Esperando número de habitación...`
- `🚗 Esperando respuesta de transporte: {user_message}`
- `🎯 Comando @select_multiple detectado`
- `✅ Sesión reanudada correctamente`
