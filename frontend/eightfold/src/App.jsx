import React, { useState } from "react";
import Home from "./pages/Home";
import InterviewPage from "./pages/InterviewPage";
import "./App.css";
export default function App() {
  const [role, setRole] = useState(null);

  const endSession = () => {
    (async () => {
      try {
        await fetch("http://127.0.0.1:8000/reset_memory", { method: "POST" });
      } catch (err) {
        console.error("Failed to notify backend to reset memory:", err);
      } finally {
        setRole(null); 
      }
    })();
  };

  if (!role) return <Home onSelectRole={(r) => setRole(r)} />;

  return <InterviewPage role={role} onEndSession={endSession} />;
}
