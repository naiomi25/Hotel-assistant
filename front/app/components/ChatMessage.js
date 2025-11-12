import React from "react";

 
const ChatMessage = ({ msg, isPausedForReceptionist, session_id, copySessionId }) => {
    const getMessageStyle = () => {
        if (msg.role === "user") {
            return "bg-blue-600 text-white self-end ml-auto";
        } else if (msg.role === "system") {
            return "bg-green-200 text-red-900 self-start border border-red-300 text-xs italic";
        } else {
            return "bg-gray-100 text-gray-800 self-start";
        }
    };

    return (
        <div className={`p-3 rounded-xl max-w-[90%] sm:max-w-[75%] ${getMessageStyle()}`}>
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
    );
};

export default ChatMessage;
