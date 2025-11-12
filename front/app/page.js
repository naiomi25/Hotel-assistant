"use client";

import React, { useRef, useEffect } from "react";
import { useChat } from "./hooks/useChat";
import { useSessionPolling } from "./hooks/useSessionPolling";
import ChatMessages from "./components/ChatMessages";
import ActivitySelector from "./components/ActivitySelector";
import ChatInput from "./components/ChatInput";

const ChatApp = () => {
  const scrollRef = useRef(null);

 
  const {
    messages,
    setMessages,
    input,
    setInput,
    state,
    setState,
    isActivitySelectionActive,
    isLoading,
    isWaitingForReceptionist,
    setIsWaitingForReceptionist,
    sendSpecialCommand,
    handleActivitySelect,
    confirmSelection,
    sendMessage,
    handleKeyDown,
    copySessionId,
  } = useChat();

  
  useSessionPolling({
    session_id: state.session_id,
    isWaitingForReceptionist,
    setState,
    setIsWaitingForReceptionist,
    setMessages,
  });

 
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const isPausedForReceptionist =
    isWaitingForReceptionist ||
    state?._interrupt ||
    state?.paused_at_node === "human_check";

  return (
    <main className="flex flex-col items-center min-h-screen bg-gray-100 p-4 sm:p-6 font-sans">
      <h1 className="text-3xl font-extrabold mb-4 text-blue-700">
        Nayra | Asistente Hotel Horizonte Azul 🌴
      </h1>

      {/*  Área del chat */}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
        scrollRef={scrollRef}
        isPausedForReceptionist={isPausedForReceptionist}
        session_id={state.session_id}
        copySessionId={copySessionId}
      />

      {/*  Botones de selección de actividades */}
      <ActivitySelector
        isActive={isActivitySelectionActive}
        availableActivities={state.available_activities}
        selectedActivities={state.selected_activities}
        onActivitySelect={handleActivitySelect}
        onConfirm={confirmSelection}
        onSkip={() => sendSpecialCommand("@none")}
      />

      {/*  Input del usuario */}
      <ChatInput
        input={input}
        setInput={setInput}
        isLoading={isLoading}
        isPausedForReceptionist={isPausedForReceptionist}
        onSend={sendMessage}
        onKeyDown={handleKeyDown}
      />
    </main>
  );
};

export default ChatApp;