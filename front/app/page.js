"use client";

import { useState, useRef, useEffect } from "react";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [state, setState] = useState({});
  const [showActivities, setShowActivities] = useState(true);
  const scrollRef = useRef(null);

  const API_URL = "http://127.0.0.1:5000";

  // 🔁 Auto-scroll al último mensaje
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // ✉️ Enviar mensaje normal
  async function sendMessage() {
    const user_message = input.trim();
    if (!user_message) return;

    const newMessages = [...messages, { role: "user", content: user_message }];
    setMessages(newMessages);
    setInput("");

    try {
      const res = await fetch(`${API_URL}/api/start_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, user_message }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);

      const data = await res.json();

      // 🧠 Mensaje principal de Nayra
      setMessages((prev) => [
        ...newMessages,
        { role: "assistant", content: data.assistant_message },
      ]);
      setState(data.state);

      // 💬 Si hay un mensaje adicional en el estado (p. ej., transporte)
      if (
        data.state?.assistant_message &&
        data.state.assistant_message !== data.assistant_message
      ) {
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.state.assistant_message },
          ]);
        }, 600);
      }

      // 📘 Si viene un PDF (guía)
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

      // ❌ Ocultar botones después de confirmar o rechazar actividades
      if (
        user_message.startsWith("@select_multiple") ||
        user_message.startsWith("@none")
      ) {
        setShowActivities(false);
      }
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...newMessages,
        { role: "assistant", content: "⚠️ Error al conectar con el servidor." },
      ]);
    }
  }

  // 🎯 Selección de actividades (solo marca o desmarca)
  function handleActivitySelect(activity) {
    const selected = state.selected_activities || [];
    const alreadySelected = selected.includes(activity);

    const updated = alreadySelected
      ? selected.filter((a) => a !== activity)
      : [...selected, activity];

    setState((prev) => ({ ...prev, selected_activities: updated }));
  }

  // ✅ Confirmar selección
  async function confirmSelection() {
    if (!state.selected_activities?.length) return;
    const payload = JSON.stringify(state.selected_activities);
    await sendSpecialCommand(`@select_multiple ${payload}`);
    setShowActivities(false); // Ocultar los botones
  }

  // 🚀 Enviar comandos especiales (@none, @select_multiple, etc.)
  async function sendSpecialCommand(command) {
    try {
      const res = await fetch(`${API_URL}/api/start_conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, user_message: command }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.assistant_message },
      ]);
      setState(data.state);

      // Mensaje adicional (transporte, etc.)
      if (
        data.state?.assistant_message &&
        data.state.assistant_message !== data.assistant_message
      ) {
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.state.assistant_message },
          ]);
        }, 600);
      }

      // PDF
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

      // Ocultar botones si corresponde
      if (
        command.startsWith("@select_multiple") ||
        command.startsWith("@none")
      ) {
        setShowActivities(false);
      }
    } catch (error) {
      console.error(error);
    }
  }

  // ⌨️ Enviar con Enter
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <main className="flex flex-col items-center min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-semibold mb-4 text-gray-800">
        Asistente del Hotel Horizonte Azul 🌞
      </h1>

      {/* 💬 Chat area */}
      <div
        ref={scrollRef}
        className="w-full max-w-2xl bg-white rounded-2xl shadow-lg p-4 flex flex-col space-y-3 overflow-y-auto h-[60vh] transition-all duration-500"
      >
        {messages.length === 0 && (
          <p className="text-center text-gray-400">
            Escribe un mensaje para comenzar la conversación.
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl max-w-[80%] transition-all duration-500 ease-in-out ${
              msg.role === "user"
                ? "bg-blue-100 self-end ml-auto animate-fadeIn"
                : "bg-gray-100 self-start animate-fadeIn"
            }`}
          >
            <p className="text-sm text-gray-800">{msg.content}</p>

            {/* 📘 Mostrar PDF si Nayra envía una guía */}
            {msg.pdf_url && (
              <div className="mt-2 transition-opacity duration-700 opacity-100">
                <iframe
                  src={msg.pdf_url}
                  className="w-full h-64 rounded-lg border shadow-sm"
                  title="Guía turística"
                ></iframe>
              </div>
            )}
          </div>
        ))}

        {/* 🎯 Mostrar botones de actividades */}
        {showActivities && state.available_activities?.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3 animate-fadeIn">
            {state.available_activities.map((act, i) => {
              const selected = state.selected_activities?.includes(act);
              return (
                <button
                  key={i}
                  onClick={() => handleActivitySelect(act)}
                  className={`text-sm px-3 py-2 rounded-xl transition-all duration-300 ${
                    selected
                      ? "bg-blue-700 text-white scale-105"
                      : "bg-blue-500 hover:bg-blue-600 text-white"
                  }`}
                >
                  {act}
                </button>
              );
            })}
            <button
              onClick={() => sendSpecialCommand("@none")}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 text-sm px-3 py-2 rounded-xl transition-all duration-300"
            >
              No me interesa ninguna
            </button>

            {state.selected_activities?.length > 0 && (
              <button
                onClick={() => confirmSelection()}
                className="bg-green-500 hover:bg-green-600 text-white text-sm px-4 py-2 rounded-xl transition-all duration-300"
              >
                Confirmar selección ✅
              </button>
            )}
          </div>
        )}
      </div>

      {/* ✍️ Input y botón de envío */}
      <div className="w-full max-w-2xl flex mt-4 space-x-2">
        <textarea
          className="flex-1 border border-gray-300 rounded-lg p-3 resize-none h-14 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
          placeholder="Escribe tu mensaje..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={sendMessage}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-all duration-300"
        >
          Enviar
        </button>
      </div>

      {/* 🧩 Debug box */}
      <div className="mt-4 w-full max-w-2xl bg-gray-100 rounded-lg p-2 text-xs overflow-auto h-32">
        <strong>Estado actual (debug):</strong>
        <pre>{JSON.stringify(state, null, 2)}</pre>
      </div>

      {/* 🎨 Animaciones */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.4s ease-out forwards;
        }
      `}</style>
    </main>
  );
}
