# Estructura Modular del Frontend

## 📁 Organización de Archivos

```
front/app/
├── page.js                      # Componente principal (refactorizado)
├── constants.js                 # Constantes globales
├── components/
│   ├── ChatMessages.js          # Área de mensajes del chat
│   ├── ChatMessage.js           # Mensaje individual (no usado actualmente)
│   ├── ActivitySelector.js     # Selector de actividades
│   └── ChatInput.js             # Input del usuario
└── hooks/
    ├── useChat.js               # Hook para lógica del chat
    └── useSessionPolling.js     # Hook para polling de sesión
```

## 🎯 Descripción de Módulos

### **page.js** - Componente Principal

Componente principal simplificado que orquesta todos los módulos. Ahora solo tiene ~50 líneas vs las 451 originales.

**Responsabilidades:**

- Inicializar los hooks personalizados
- Manejar el auto-scroll de mensajes
- Renderizar el layout principal

---

### **constants.js** - Constantes

Centraliza todas las constantes de configuración.

**Contenido:**

- `API_URL`: URL del backend Flask
- `POLLING_INTERVAL`: Intervalo de polling (7000ms)

---

### **hooks/useChat.js** - Lógica del Chat

Hook personalizado que maneja toda la lógica del chat y estado.

**Responsabilidades:**

- Gestión de mensajes y estado de la conversación
- Llamadas a la API del backend
- Manejo de session_id y sessionStorage
- Lógica de selección de actividades
- Manejo de interrupciones (recepcionista)

**Retorna:**

- `messages`, `setMessages`: Estado de mensajes
- `input`, `setInput`: Texto del input
- `state`, `setState`: Estado global de la conversación
- `isActivitySelectionActive`: Flag de selección activa
- `isLoading`: Estado de carga
- `isWaitingForReceptionist`: Flag de espera de recepcionista
- Funciones: `sendMessage`, `handleKeyDown`, `confirmSelection`, etc.

---

### **hooks/useSessionPolling.js** - Polling de Sesión

Hook personalizado para el polling del estado de sesión cuando se espera confirmación del recepcionista.

**Responsabilidades:**

- Consultar el endpoint `/api/status/:session_id` cada 7 segundos
- Detectar cuando la sesión es completada
- Actualizar mensajes y estado cuando hay respuesta
- Limpiar el intervalo cuando no es necesario

**Parámetros:**

- `session_id`: ID de la sesión actual
- `isWaitingForReceptionist`: Flag de espera
- `setState`, `setIsWaitingForReceptionist`, `setMessages`: Setters

---

### **components/ChatMessages.js** - Área de Mensajes

Componente que renderiza toda el área de mensajes del chat.

**Props:**

- `messages`: Array de mensajes
- `isLoading`: Estado de carga
- `scrollRef`: Referencia para auto-scroll
- `isPausedForReceptionist`: Flag de pausa
- `session_id`: ID de sesión
- `copySessionId`: Función para copiar session_id

**Características:**

- Muestra placeholder cuando no hay mensajes
- Renderiza mensajes de usuario, asistente y sistema con estilos diferentes
- Muestra session_id en mensajes de interrupción
- Muestra enlaces a PDFs
- Indicador de carga animado

---

### **components/ActivitySelector.js** - Selector de Actividades

Componente para la selección de actividades turísticas.

**Props:**

- `isActive`: Si el selector está activo
- `availableActivities`: Array de actividades disponibles
- `selectedActivities`: Array de actividades seleccionadas
- `onActivitySelect`: Callback para seleccionar/deseleccionar
- `onConfirm`: Callback para confirmar selección
- `onSkip`: Callback para saltar selección

**Características:**

- Botones toggleables con animaciones
- Botón de confirmación (solo habilitado si hay selección)
- Botón para saltar la selección

---

### **components/ChatInput.js** - Input del Usuario

Componente para el área de entrada de texto del usuario.

**Props:**

- `input`: Valor del textarea
- `setInput`: Setter del input
- `isLoading`: Estado de carga
- `isPausedForReceptionist`: Flag de pausa
- `onSend`: Callback para enviar mensaje
- `onKeyDown`: Callback para teclas

**Características:**

- Se oculta cuando está pausado para el recepcionista
- Textarea con placeholder dinámico
- Botón de envío con estados disabled
- Soporte para Enter (sin Shift) para enviar

---

## 🔄 Flujo de Datos

```
page.js
  ├─> useChat()
  │     ├─> Gestiona messages, state, input
  │     ├─> handleApiCall() → Backend Flask
  │     └─> Retorna funciones y estados
  │
  ├─> useSessionPolling()
  │     ├─> Inicia/detiene polling
  │     └─> Actualiza state cuando completa
  │
  ├─> ChatMessages
  │     └─> Renderiza todos los mensajes
  │
  ├─> ActivitySelector
  │     └─> Permite seleccionar actividades
  │
  └─> ChatInput
        └─> Captura input del usuario
```

## ✅ Beneficios de la Modularización

1. **Mantenibilidad**: Cada módulo tiene una responsabilidad clara
2. **Reutilización**: Los componentes y hooks son reutilizables
3. **Testing**: Más fácil testear módulos independientes
4. **Legibilidad**: Código más limpio y fácil de entender
5. **Escalabilidad**: Fácil agregar nuevas funcionalidades

## 🚀 Sin Cambios en la Lógica

Toda la funcionalidad original se mantiene intacta:

- ✅ Session management
- ✅ Polling de interrupciones
- ✅ Selección de actividades
- ✅ Manejo de mensajes
- ✅ Auto-scroll
- ✅ Estados de carga
- ✅ Integración con backend Flask

La refactorización es **puramente estructural**, sin cambios en el comportamiento.
