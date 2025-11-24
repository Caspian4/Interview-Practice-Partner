import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import axios from "axios";
import { ReactMediaRecorder } from "react-media-recorder";
import ChatBubble from "../components/ChatBubble";
import "./Interview.css";

export default function InterviewPage({ role, onEndSession }) {
  const [mode, setMode] = useState("voice");
  const [messages, setMessages] = useState([]);
  const [textInput, setTextInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const greetedOnce = useRef(false);
  const [userEntries, setUserEntries] = useState(0);
  const [feedbackOverlay, setFeedbackOverlay] = useState(null);

  const base64ToBlob = (base64) => {
    const bytes = atob(base64);
    const arr = new Uint8Array([...bytes].map((c) => c.charCodeAt(0)));
    return new Blob([arr], { type: "audio/mp3" });
  };

// Auto scroll whenever messages change
useEffect(() => {
  if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  }
}, [messages]);
  useEffect(() => {
    if (greetedOnce.current) return;
    greetedOnce.current = true;

    async function loadGreeting() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/greet", {
          params: { mode, role },
        });

        const { text, audio_base64 } = res.data;

        if (mode === "text") {
          setMessages([{ role: "assistant", text }]);
        } else {
          const blob = base64ToBlob(audio_base64);
          const url = URL.createObjectURL(blob);
          setMessages([{ role: "assistant", text, audioUrl: url }]);
        }
      } catch {
        setMessages([{ role: "assistant", text: "Hello! Let's begin your interview." }]);
      }
    }

    loadGreeting();
  }, [mode, role]);

  const sendText = async () => {
    if (!textInput.trim()) return;

    const msg = textInput;
    setTextInput("");
    setMessages((p) => [...p, { role: "user", text: msg }]);
    setUserEntries((prev) => prev + 1);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chattext", {
        query: msg,
        role: role,
      });
      setMessages((p) => [...p, { role: "assistant", text: res.data.answer }]);
    } catch {
      setMessages((p) => [...p, { role: "assistant", text: "Backend error" }]);
    }
  };

  const uploadAudio = async (audioBlob) => {
    const form = new FormData();
    form.append("file", audioBlob, "user.wav");
    form.append("role", role);

    setMessages((p) => [...p, { role: "user", text: "…processing…" }]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/voice_chat", form);
      const { transcript, answer, audio_base64 } = res.data;

      setMessages((prev) =>
        prev.map((m, i) => (i === prev.length - 1 ? { role: "user", text: transcript } : m))
      );
      setUserEntries((prev) => prev + 1);

      const blob = base64ToBlob(audio_base64);
      const url = URL.createObjectURL(blob);

      setMessages((p) => [...p, { role: "assistant", text: answer, audioUrl: url }]);
    } catch {
      setMessages((p) => [...p, { role: "assistant", text: "Backend error" }]);
    }
  };

  const dismissFeedback = () => setFeedbackOverlay(null);

  const handleEndInterview = async () => {
    if (userEntries < 4) {
      setMessages((p) => [
        ...p,
        { role: "assistant", text: `Please answer at least ${4 - userEntries} more question(s) before ending the interview.` },
      ]);
      return;
    }

    try {
      const res = await axios.post("http://127.0.0.1:8000/end_interview");
      setFeedbackOverlay(res.data.feedback);
    } catch {
      setFeedbackOverlay("Could not generate interview feedback.");
    }
  };

  const handleEndSession = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/reset_memory");
    } catch (err) {
      console.log("Memory reset failed.", err);
    }

    setMessages([]);
    onEndSession();
  };
  

  return (
    <div className="interview-page-container">
      <div className="top-bar">
        <h2 className="role-title">Interviewing for: {role}</h2>
      </div>

      {feedbackOverlay && (
        <>
          <div className="overlay-backdrop" onClick={dismissFeedback}></div>
          <div className="feedback-sheet" role="dialog" aria-modal="true">
            <div className="sheet-header">
              <h3>Interview Feedback</h3>
              <div className="sheet-actions">
                <button className="close-sheet-btn" onClick={dismissFeedback} aria-label="Close feedback">
                  Close
                </button>
              </div>
            </div>
            <div className="sheet-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {typeof feedbackOverlay === "string" ? feedbackOverlay : String(feedbackOverlay)}
              </ReactMarkdown>
              <div className="sheet-footer">
                <button className="end-session-btn" onClick={handleEndSession}>
                  🔚 End Session
                </button>
                <button className="prominent-end" onClick={() => { handleEndSession(); dismissFeedback(); }}>
                  Finish & Close
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      <div className="content-area">
        <aside className="sidebar">
          <div className="panel">
            <h4 style={{ margin: 0, marginBottom: 8 }}>Mode</h4>
            <div className="mode-tabs" style={{ justifyContent: "flex-start" }}>
              <button onClick={() => setMode("text")} className={mode === "text" ? "tab active" : "tab"} style={{ width: "100%" }}>Text</button>
              <button onClick={() => setMode("voice")} className={mode === "voice" ? "tab active" : "tab"} style={{ width: "100%" }}>Voice</button>
            </div>
          </div>

          <div className="panel">
            <h4 style={{ margin: 0, marginBottom: 8 }}>Controls</h4>
            <div style={{ marginBottom: 8 }}><strong>Answers:</strong> {userEntries}/4</div>
            <button className="end-session-btn" onClick={handleEndSession} style={{ width: "100%", marginBottom: 8 }}>🔚 End Session</button>
            <button
              className="end-interview-btn"
              onClick={handleEndInterview}
              style={{ width: "100%" }}
              disabled={userEntries < 4}
              title={userEntries < 4 ? `Answer ${4 - userEntries} more question(s)` : 'End the interview'}
            >
              📝 End Interview
            </button>
          </div>
        </aside>

        <main className="main">
          <div className="chat-container">
            <div className="chat-window glass-card">
              {messages.map((msg, idx) => (
                <ChatBubble key={idx} msg={msg} />
              ))}
              <div ref={messagesEndRef}></div>
            </div>

            <div className="input-area">
              {mode === "text" && (
                <div className="text-mode">
                  <textarea
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    placeholder="Type your message..."
                  />
                  <button onClick={sendText} className="send-btn">Send</button>
                </div>
              )}
              {mode === "voice" && (
                <ReactMediaRecorder
                  audio
                  onStop={(url, blob) => uploadAudio(blob)}
                  render={({ startRecording, stopRecording }) => (
                    <div className="voice-controls">
                      {!isRecording ? (
                        <button className="record-btn" onClick={() => { startRecording(); setIsRecording(true); }}>🎙 Start Recording</button>
                      ) : (
                        <button className="stop-btn" onClick={() => { stopRecording(); setIsRecording(false); }}>⏹ Stop & Send</button>
                      )}
                    </div>
                  )}
                />
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
