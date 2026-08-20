import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { listResumes, uploadResume } from "../services/resumeService";

const STATUS_TONE = {
  succeeded: "good",
  pending: "mid",
  failed: "low",
};

export default function Dashboard() {
  const [resumes, setResumes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadResumes();
  }, []);

  async function loadResumes() {
    setIsLoading(true);
    try {
      const data = await listResumes();
      setResumes(data);
    } catch {
      setError("Couldn't load your resumes. Try refreshing.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setIsUploading(true);
    try {
      await uploadResume(file);
      await loadResumes();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Only PDF and DOCX are supported.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 64 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1>Your resumes</h1>
          <p style={{ margin: 0, color: "var(--color-text-muted)" }}>
            Upload a resume to get an ATS score and match it against a job.
          </p>
        </div>

        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            style={{ display: "none" }}
            id="resume-upload-input"
          />
          <label htmlFor="resume-upload-input" className="btn btn-primary" style={{ cursor: "pointer" }}>
            {isUploading ? "Uploading..." : "Upload resume"}
          </label>
        </div>
      </div>

      {error && <p className="error-text" style={{ marginTop: 16 }}>{error}</p>}

      <div style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 12 }}>
        {isLoading && <p style={{ color: "var(--color-text-muted)" }}>Loading...</p>}

        {!isLoading && resumes.length === 0 && (
          <div className="card" style={{ textAlign: "center", padding: 48 }}>
            <h3>No resumes yet</h3>
            <p style={{ color: "var(--color-text-muted)" }}>
              Upload a PDF or DOCX resume to get started.
            </p>
          </div>
        )}

        {resumes.map((resume) => (
          <Link
            key={resume.id}
            to={`/resumes/${resume.id}`}
            className="card"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div>
              <h3 style={{ margin: 0 }}>{resume.original_filename}</h3>
              <p style={{ margin: "4px 0 0", fontSize: "0.82rem", color: "var(--color-text-muted)" }}>
                Uploaded {new Date(resume.created_at).toLocaleDateString()}
              </p>
            </div>
            <span className={`badge badge-${STATUS_TONE[resume.parsing_status] || "neutral"}`}>
              {resume.parsing_status}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}