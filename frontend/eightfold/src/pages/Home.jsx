import React, { useState } from "react";
import axios from "axios";
import "./Home.css";

export default function Home({ onSelectMode, onSelectRole }) {
  const [uploading, setUploading] = useState(false);
  const [autoRole, setAutoRole] = useState(null);

  const roles = [
    { name: "Software Engineer", icon: "💻" },
    { name: "Sales Executive", icon: "💼" },
  ];

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const form = new FormData();
    form.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:8000/upload_resume", form);
      if (res.status === 200) {
        setAutoRole("resume-role"); // (Resume parsed internally)
        onSelectRole("resume-role");
      }
    } catch (error) {
      console.error(error);
      alert("Resume upload failed");
    }
    setUploading(false);
  };

  return (
    <div className="home-wrapper">
      <h1 className="home-title">AI Interview</h1>
      <p className="home-sub">Choose a role or upload your resume</p>

      {/* Resume upload */}
      <div className="resume-box">
        <label className="upload-btn">
          📄 Upload Resume
          <input
            type="file"
            accept="application/pdf"
            onChange={handleResumeUpload}
            hidden
          />
        </label>

        {uploading && <p>Analyzing resume...</p>}
        {autoRole && <p className="success-msg">✓ Role auto-detected from resume</p>}
      </div>

      {/* Role selection */}
      {!autoRole && (
        <>
          <h2 className="section-title">Select Interview Role</h2>
          <div className="role-grid">
            {roles.map((role) => (
              <div
                key={role.name}
                className="role-card"
                onClick={() => onSelectRole(role.name)}
              >
                <div className="role-icon">{role.icon}</div>
                <div className="role-text">{role.name}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Only show mode cards once role selected */}
      {autoRole || (
        <p className="note">* Role selection required before continuing</p>
      )}
    </div>
  );
}
