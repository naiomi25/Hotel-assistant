# 🏨 Hotel Assistant - Nayra

Asistente virtual inteligente para Hotel Horizonte Azul, construido con LangGraph, Flask y Next.js.

## 🚀 Inicio Rápido

### Backend (Flask + LangGraph)

```bash
# Instalar dependencias
pip install -r librerias.txt

# Levantar servidor
python app.py
```

**URL**: http://127.0.0.1:5000

### Frontend (Next.js)

```bash
# Instalar dependencias
cd front
npm install  # o pnpm install

# Levantar servidor
npm run dev  # o pnpm dev
```

**URL**: http://localhost:3000

## 📁 Estructura del Proyecto

```
hotel-assistant/
├── app/                          # Backend Flask
│   ├── api/                      # Rutas API (modular)
│   │   ├── routes.py            # Blueprint principal
│   │   ├── status_route.py      # GET /status/<session_id>
│   │   ├── start_conversation_route.py  # POST /start_conversation
│   │   ├── resume_route.py      # POST /resume
│   │   └── utils.py             # Utilidades compartidas
│   ├── nodes/                    # Nodos de LangGraph
│   ├── prompts/                  # Prompts del LLM
│   ├── state/                    # Estado de la conversación
│   ├── services/                 # Servicios externos (clima, etc.)
│   └── graph.py                  # Definición del grafo LangGraph
│
├── front/                        # Frontend Next.js
│   └── app/
│       ├── page.js              # Componente principal
│       ├── constants.js         # Configuración
│       ├── components/          # Componentes UI (modular)
│       │   ├── ChatMessages.js
│       │   ├── ActivitySelector.js
│       │   └── ChatInput.js
│       └── hooks/               # Hooks personalizados
│           ├── useChat.js
│           └── useSessionPolling.js
│
├── app.py                       # Punto de entrada Flask
└── librerias.txt               # Dependencias Python
```

## 🔧 Tecnologías

**Backend:**

- Flask (API REST)
- LangGraph (flujo conversacional)
- LangChain + OpenAI GPT-4o-mini
- Python 3.x

**Frontend:**

- Next.js 16
- React 19
- Tailwind CSS

## 📡 API Endpoints

| Método | Endpoint                   | Descripción                       |
| ------ | -------------------------- | --------------------------------- |
| POST   | `/api/start_conversation`  | Inicia/continúa conversación      |
| POST   | `/api/resume`              | Reanuda conversación interrumpida |
| GET    | `/api/status/<session_id>` | Consulta estado de sesión         |

## ⚙️ Características

- ✅ Gestión de sesiones persistentes
- ✅ Selección de actividades turísticas
- ✅ Consulta de clima en tiempo real
- ✅ Human-in-the-loop (validación de recepcionista)
- ✅ Generación de guías turísticas en PDF
- ✅ Manejo de transporte
- ✅ Arquitectura modular y escalable

## 🌐 Variables de Entorno

Crear un archivo `.env` en la raíz con:

```env
OPENAI_API_KEY=tu_api_key_aqui
WEATHER_API_KEY=tu_weather_api_key  # Opcional
```

## 📚 Documentación

- **Frontend**: Ver `front/MODULAR_STRUCTURE.md`
- **Backend API**: Ver `app/api/API_STRUCTURE.md`

## 🧪 Flujo de Conversación

1. Usuario inicia conversación
2. Asistente solicita número de habitación
3. Consulta clima actual
4. Sugiere actividades según clima
5. Usuario selecciona actividades
6. Recepcionista valida disponibilidad (interrupt)
7. Asistente ofrece transporte
8. Genera guía turística PDF

## 👨‍💻 Desarrollo

El proyecto está completamente modularizado:

- Cada ruta de la API en su propio archivo
- Componentes y hooks reutilizables en el frontend
- Funcionalidad sin cambios, solo mejor organización

---

**Branch actual**: `feature/api`
