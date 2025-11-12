import { useState, useCallback, useEffect } from "react";
import { API_URL } from "../constants";

/**
 * Hook personalizado para manejar la lógica del chat:
 * - Mensajes y estado de la conversación
 * - Llamadas a la API
 * - Selección de actividades
 * - Gestión del session_id
 */
export const useChat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [state, setState] = useState({ session_id: null });
    const [isActivitySelectionActive, setIsActivitySelectionActive] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isWaitingForReceptionist, setIsWaitingForReceptionist] = useState(false);

    // Recuperar session_id del sessionStorage al cargar
    useEffect(() => {
        if (typeof window !== "undefined") {
            const savedSession = sessionStorage.getItem("session_id");
            if (savedSession) {
                setState((prev) => ({ ...prev, session_id: savedSession }));
            }
        }
    }, []);

    const handleApiCall = useCallback(
        async (user_message, is_user_input = true) => {
            if (!user_message.trim()) return;
            setIsLoading(true);

            const newMessages = is_user_input
                ? [...messages, { role: "user", content: user_message }]
                : messages;

            if (is_user_input) setMessages(newMessages);
            setInput("");

            try {
                console.log("🔍 Estado completo antes de enviar:", {
                    waiting_for_transport: state.waiting_for_transport,
                    waiting_for_room: state.waiting_for_room,
                    session_id: state.session_id,
                    user_message: user_message,
                    full_state: state,
                });

                const res = await fetch(`${API_URL}/api/start_conversation`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ state, user_message }),
                });

                if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);

                const data = await res.json();

                // 💫 Pequeña pausa para asegurar que React renderiza en orden
                await new Promise((resolve) => setTimeout(resolve, 400));

                // ⭐ Guardar o recuperar el session_id
                console.log("📋 Session ID:", data.session_id || data.state?.session_id);
                setState(data.state);
                if (data.state?.session_id) {
                    sessionStorage.setItem("session_id", data.state.session_id);
                } else if (data.session_id) {
                    sessionStorage.setItem("session_id", data.session_id);
                }

                // 💡 Reinyectar el session_id si el backend no lo devuelve
                setState((prev) => ({
                    ...data.state,
                    session_id:
                        data.state?.session_id ||
                        data.session_id ||
                        sessionStorage.getItem("session_id"),
                }));

                // 🛑 Si hay INTERRUPT (recepcionista)
                if (data.status === "interrupted") {
                    console.log(
                        "🛑 INTERRUPT detectado, activando polling...",
                        data.session_id || data.state?.session_id
                    );
                    setMessages((prev) => [
                        ...newMessages,
                        {
                            role: "system",
                            content:
                                data.assistant_message ||
                                "🛑 Esperando confirmación del recepcionista...",
                            isInterrupt: true,
                            session_id: data.session_id || data.state?.session_id,
                        },
                    ]);
                    setIsActivitySelectionActive(false);
                    setIsWaitingForReceptionist(true);
                    setIsLoading(false);
                    return;
                }

                // ✅ Flujo normal
                const backendMessages = data.state?.messages || [];
                const isResumeResponse = data.status === "resumed";
                const existingContents = new Set(messages.map((m) => m.content));

                const newAssistantMessages = backendMessages
                    .filter((msg) => {
                        if (msg.role !== "assistant") return false;
                        if (isResumeResponse) return true; // mostrar todo al reanudar
                        return !existingContents.has(msg.content);
                    })
                    .map((msg) => ({
                        role: "assistant",
                        content: msg.content,
                    }));

                console.log("🧩 Mensajes del backend:", newAssistantMessages);

                // 💬 Añadir todos los mensajes nuevos en orden correcto
                setMessages((prev) => [...prev, ...newAssistantMessages]);

                // Agregar mensaje final explícito si no está duplicado
                if (data.assistant_message && !existingContents.has(data.assistant_message)) {
                    setMessages((prev) => [
                        ...prev,
                        { role: "assistant", content: data.assistant_message },
                    ]);
                }

                // Activar selección si aplica
                const hasActivities = data.state?.available_activities?.length > 0;
                setIsActivitySelectionActive(
                    hasActivities && !data.state?.paused_at_node
                );

                // Mostrar PDF si existe
                if (data.pdf_url) {
                    setTimeout(() => {
                        setMessages((prev) => [
                            ...prev,
                            {
                                role: "assistant",
                                content: "📘 Aquí tienes la guía turística:",
                                pdf_url: data.pdf_url,
                            },
                        ]);
                    }, 500);
                }
            } catch (error) {
                console.error("Error en la API:", error);
                setMessages((prev) => [
                    ...newMessages,
                    {
                        role: "assistant",
                        content: `⚠️ Error: ${error.message}`,
                    },
                ]);
            } finally {
                setIsLoading(false);
            }
        },
        [messages, state]
    );

    const sendSpecialCommand = (command, shouldBeDisplayed = false) => {
        if (shouldBeDisplayed) {
            setMessages((prev) => [
                ...prev,
                { role: "user", content: "Confirmando actividades..." },
            ]);
        }
        setIsActivitySelectionActive(false);
        handleApiCall(command, false);
    };

    const handleActivitySelect = (activity) => {
        const selected = state.selected_activities || [];
        const alreadySelected = selected.includes(activity);
        const updated = alreadySelected
            ? selected.filter((a) => a !== activity)
            : [...selected, activity];
        setState((prev) => ({ ...prev, selected_activities: updated }));
    };

    const confirmSelection = () => {
        if (!state.selected_activities?.length) return;
        const payload = JSON.stringify(state.selected_activities);
        sendSpecialCommand(`@select_multiple ${payload}`, true);
    };

    const sendMessage = () => handleApiCall(input, true);

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const copySessionId = () => {
        const session_id = state.session_id;
        if (session_id) {
            navigator.clipboard.writeText(session_id);
            alert("✅ Session ID copiado al portapapeles");
        }
    };

    return {
        messages,
        setMessages,
        input,
        setInput,
        state,
        setState,
        isActivitySelectionActive,
        setIsActivitySelectionActive,
        isLoading,
        isWaitingForReceptionist,
        setIsWaitingForReceptionist,
        handleApiCall,
        sendSpecialCommand,
        handleActivitySelect,
        confirmSelection,
        sendMessage,
        handleKeyDown,
        copySessionId,
    };
};
