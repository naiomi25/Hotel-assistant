import React from "react";


const ChatInput = ({
    input,
    setInput,
    isLoading,
    isPausedForReceptionist,
    onSend,
    onKeyDown,
}) => {
    if (isPausedForReceptionist) return null;

    return (
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
                onKeyDown={onKeyDown}
                disabled={isLoading}
            />
            <button
                onClick={onSend}
                disabled={isLoading || !input.trim()}
                className={`px-6 py-2 rounded-xl text-lg font-bold ${isLoading || !input.trim()
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-blue-600 hover:bg-blue-700 text-white"
                    }`}
            >
                Enviar
            </button>
        </div>
    );
};

export default ChatInput;
