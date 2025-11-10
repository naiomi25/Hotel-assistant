"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";

const API_URL = "http://127.0.0.1:5000";

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [state, setState] = useState({});
  const [isActivitySelectionActive, setIsActivitySelectionActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [isWaitingForReceptionist, setIsWaitingForReceptionist] = useState(false);
  const scrollRef = useRef(null);
  const pollingRef = useRef(null);

  const session_id = state.session_id || null;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // ⭐ FUNCIÓN PARA VERIFICAR ESTADO DE LA SESIÓN
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
  }, [session_id, isWaitingForReceptionist]);

  // ⭐ INICIAR/DETENER POLLING
  useEffect(() => {
    if (isWaitingForReceptionist && session_id) {
      console.log("🔄 Iniciando polling para session:", session_id);
      pollingRef.current = setInterval(checkSessionStatus, 3000); // Cada 3 segundos
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
        const res = await fetch(`${API_URL}/api/start_conversation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ state, user_message }),
        });

        if (!res.ok)
          throw new Error(`Error ${res.status}: ${res.statusText}`);

        const data = await res.json();
        
        // ⭐ GUARDAR SIEMPRE EL SESSION_ID
        console.log("📋 Session ID:", data.session_id || data.state?.session_id);
        setState(data.state);

        // 🛑 Si hay INTERRUPT
        if (data.status === "interrupted") {
          console.log("🛑 INTERRUPT detectado, activando polling...", data.session_id || data.state?.session_id);
          setMessages((prev) => [
            ...newMessages,
            {
              role: "system",
              content: data.assistant_message || "🛑 Esperando confirmación del recepcionista...",
              isInterrupt: true,
              session_id: data.session_id || data.state?.session_id
            },
          ]);
          setIsActivitySelectionActive(false);
          setIsWaitingForReceptionist(true); // ⭐ ACTIVAR POLLING
          console.log("✅ isWaitingForReceptionist activado");
          setIsLoading(false);
          return;
        }

        // ✅ Flujo normal
        const assistantMessage = {
          role: "assistant",
          content: data.assistant_message,
        };
        setMessages((prev) => [...newMessages, assistantMessage]);

        const hasActivities = data.state?.available_activities?.length > 0;
        setIsActivitySelectionActive(hasActivities && !data.state?.paused_at_node);

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

  // ⭐ Copiar session_id al portapapeles
  const copySessionId = () => {
    if (session_id) {
      navigator.clipboard.writeText(session_id);
      alert("✅ Session ID copiado al portapapeles");
    }
  };

  const isPausedForReceptionist = isWaitingForReceptionist || state?._interrupt || state?.paused_at_node === "human_check";

  return (
    <main className="flex flex-col items-center min-h-screen bg-gray-100 p-4 sm:p-6 font-sans">
      <h1 className="text-3xl font-extrabold mb-4 text-blue-700">
        Nayra | Asistente Hotel Horizonte Azul 🌴
      </h1>

      {/* ⭐ INDICADOR MEJORADO CON SESSION_ID */}
      {isPausedForReceptionist && session_id && (
        <div className="w-full max-w-2xl mt-4 p-4 bg-yellow-50 border-2 border-yellow-400 rounded-xl shadow-lg text-center">
          <p className="text-lg font-bold text-yellow-900 mb-2">
            🛑 PAUSA ACTIVA: Esperando confirmación del recepcionista
          </p>
          <p className="text-sm text-yellow-800 mb-3">
            El recepcionista debe validar la disponibilidad usando este código:
          </p>
          <div className="flex items-center justify-center gap-2">
            <code className="bg-yellow-200 px-4 py-2 rounded-lg text-sm font-mono font-bold text-yellow-900 border border-yellow-300">
              {session_id}
            </code>
            <button
              onClick={copySessionId}
              className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-2 rounded-lg text-sm font-semibold transition"
            >
              📋 Copiar
            </button>
          </div>
        </div>
      )}

      {/* 💬 Área del chat */}
      <div
        ref={scrollRef}
        className="w-full max-w-2xl bg-white rounded-xl shadow-2xl p-4 flex flex-col space-y-3 overflow-y-auto h-[70vh] border border-gray-200"
      >
        {messages.length === 0 && (
          <p className="text-center text-gray-400 mt-20">
            Escribe un mensaje para que Nayra, nuestra recepcionista virtual, te atienda.
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl max-w-[90%] sm:max-w-[75%] ${
              msg.role === "user"
                ? "bg-blue-600 text-white self-end ml-auto"
                : msg.role === "system"
                ? "bg-red-200 text-red-900 self-start border border-red-300 text-xs italic"
                : "bg-gray-100 text-gray-800 self-start"
            }`}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {msg.content}
            </p>

            {/* ⭐ Mostrar session_id en el mensaje de interrupt */}
            {msg.isInterrupt && msg.session_id && (
              <div className="mt-3 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs">
                <p className="font-semibold text-yellow-900 mb-1">
                  🔑 Código para recepcionista:
                </p>
                <code className="text-yellow-800 font-mono">
                  {msg.session_id}
                </code>
              </div>
            )}

            {msg.pdf_url && (
              <a
                href={msg.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 block text-sm font-semibold text-blue-600 hover:text-blue-800"
              >
                Abrir Guía Turística 🗺️
              </a>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center space-x-2 self-start bg-gray-100 p-3 rounded-xl animate-pulse">
            <span className="h-2 w-2 bg-blue-500 rounded-full"></span>
            <span className="h-2 w-2 bg-blue-500 rounded-full delay-100"></span>
            <span className="h-2 w-2 bg-blue-500 rounded-full delay-200"></span>
            <p className="text-xs text-gray-600 ml-2">Nayra está pensando...</p>
          </div>
        )}
      </div>

      {/* 🎯 Botones de selección de actividades */}
      {isActivitySelectionActive && state.available_activities?.length > 0 && (
        <div className="w-full max-w-2xl bg-white p-3 rounded-b-xl border-t border-gray-200 shadow-xl -mt-1 flex flex-col gap-2">
          <p className="text-sm font-medium text-gray-600">Elige tus planes:</p>
          <div className="flex flex-wrap gap-2">
            {state.available_activities.map((act, i) => {
              const selected = state.selected_activities?.includes(act);
              return (
                <button
                  key={i}
                  onClick={() => handleActivitySelect(act)}
                  className={`text-sm px-3 py-1.5 rounded-full font-medium transition-all duration-200 ${
                    selected
                      ? "bg-emerald-500 text-white scale-[1.02]"
                      : "bg-blue-100 hover:bg-blue-200 text-blue-700"
                  }`}
                >
                  {selected ? `✅ ${act}` : act}
                </button>
              );
            })}
          </div>

          <div className="flex justify-end space-x-2 pt-2 border-t mt-2 border-gray-100">
            <button
              onClick={() => sendSpecialCommand("@none")}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 text-sm px-3 py-1.5 rounded-full"
            >
              Prefiero no seleccionar nada
            </button>

            <button
              onClick={confirmSelection}
              disabled={!state.selected_activities?.length}
              className={`text-white text-sm px-4 py-1.5 rounded-full font-semibold ${
                state.selected_activities?.length
                  ? "bg-blue-700 hover:bg-blue-800"
                  : "bg-blue-400 cursor-not-allowed opacity-70"
              }`}
            >
              Confirmar Reserva
            </button>
          </div>
        </div>
      )}

      {/* ✍️ Input del usuario */}
      {!isPausedForReceptionist && (
        <div className="w-full max-w-2xl flex mt-4 space-x-2">
          <textarea
            className="flex-1 border border-gray-300 rounded-xl p-3 resize-none h-12 text-base text-black"
            placeholder={
              isLoading
                ? "Esperando respuesta de Nayra..."
                : "Escribe tu mensaje..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className={`px-6 py-2 rounded-xl text-lg font-bold ${
              isLoading || !input.trim()
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            Enviar
          </button>
        </div>
      )}

      {/* 🧩 Debug */}
      <div className="mt-4 w-full max-w-2xl">
        <button
          onClick={() => setShowDebug(!showDebug)}
          className="text-xs text-gray-600 hover:text-blue-600 mb-1"
        >
          {showDebug ? "Ocultar Estado (Debug)" : "Mostrar Estado (Debug)"}
        </button>
        {showDebug && (
          <div className="bg-gray-800 text-green-400 rounded-lg p-3 text-xs overflow-x-auto">
            <pre>{JSON.stringify(state, null, 2)}</pre>
          </div>
        )}
      </div>
    </main>
  );
};

export default ChatApp;