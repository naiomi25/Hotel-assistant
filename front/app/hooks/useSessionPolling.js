import { useEffect, useCallback, useRef } from "react";
import { API_URL, POLLING_INTERVAL } from "../constants";


//   Hook personalizado para manejar el polling del estado de sesión


export const useSessionPolling = ({
    session_id,
    isWaitingForReceptionist,
    setState,
    setIsWaitingForReceptionist,
    setMessages,
}) => {
    const pollingRef = useRef(null);

    const checkSessionStatus = useCallback(async () => {
        if (!session_id || !isWaitingForReceptionist) {
            console.log("❌ Polling cancelado:", { session_id, isWaitingForReceptionist });
            return;
        }

        console.log("🔄 Polling session status...", session_id);

        try {
            const res = await fetch(`${API_URL}/api/status/${session_id}`, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });

            if (!res.ok) {
                console.error("❌ Error en status request:", res.status);
                return;
            }

            const data = await res.json();
            console.log("📊 Status response:", data.status, data.has_interrupt);

            if (data.status === "completed") {
                console.log("✅ Sesión completada por recepcionista!");

                // Actualizar estado
                setState(data.state || {});
                setIsWaitingForReceptionist(false);

                // Añadir mensaje del asistente
                if (data.assistant_message) {
                    setMessages((prev) => [
                        ...prev,
                        {
                            role: "assistant",
                            content: data.assistant_message,
                        },
                    ]);
                }

                // Mostrar PDF si está disponible
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

                // Detener polling
                if (pollingRef.current) {
                    clearInterval(pollingRef.current);
                    pollingRef.current = null;
                }
            }
        } catch (error) {
            console.error("Error verificando estado:", error);
        }
    }, [session_id, isWaitingForReceptionist, setState, setIsWaitingForReceptionist, setMessages]);

    useEffect(() => {
        if (isWaitingForReceptionist && session_id) {
            console.log("🔄 Iniciando polling para session:", session_id);
            pollingRef.current = setInterval(checkSessionStatus, POLLING_INTERVAL);
        } else {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
                pollingRef.current = null;
            }
        }

        return () => {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
            }
        };
    }, [isWaitingForReceptionist, session_id, checkSessionStatus]);

    return { checkSessionStatus };
};
