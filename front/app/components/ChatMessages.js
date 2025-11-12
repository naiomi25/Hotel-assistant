import React from "react";

/**
 * Componente para mostrar el área de mensajes del chat
 */
const ChatMessages = ({ messages, isLoading, scrollRef, isPausedForReceptionist, session_id, copySessionId }) => {
    return (
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
                    className={`p-3 rounded-xl max-w-[90%] sm:max-w-[75%] ${msg.role === "user"
                            ? "bg-blue-600 text-white self-end ml-auto"
                            : msg.role === "system"
                                ? "bg-green-200 text-red-900 self-start border border-red-300 text-xs italic"
                                : "bg-gray-100 text-gray-800 self-start"
                        }`}
                >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {msg.content}
                    </p>

                    {/*  Mostrar session_id en el mensaje de interrupt */}
                    {msg.isInterrupt && msg.session_id && isPausedForReceptionist && (
                        <div className="mt-3 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs">
                            <code className="bg-yellow-200 px-4 py-2 rounded-lg text-sm font-mono font-bold text-yellow-900 border border-yellow-300">
                                {session_id}
                            </code>
                            <button
                                onClick={copySessionId}
                                className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-2 rounded-lg text-sm font-semibold transition">
                                📋 Copiar
                            </button>
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
    );
};

export default ChatMessages;
