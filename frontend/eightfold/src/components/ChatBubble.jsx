import React from "react";
import ReactMarkdown from "react-markdown";

export default function ChatBubble({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div className={`chat-row ${isUser ? "right" : "left"}`}>
      {!isUser && <div className="ai-icon">AI</div>}

      <div className={`chat-bubble ${isUser ? "user" : "ai"}`}>
        {/* Render text with Markdown support */}
        <ReactMarkdown>{msg.text}</ReactMarkdown>

        {/* Audio playback if available */}
        {msg.audioUrl && <audio src={msg.audioUrl} autoPlay controls />}
      </div>
    </div>
  );
}
