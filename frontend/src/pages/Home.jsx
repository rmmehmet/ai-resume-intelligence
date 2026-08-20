import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="container" style={{ paddingTop: 72, paddingBottom: 72 }}>
      <div style={{ maxWidth: 640 }}>
        <span className="badge badge-neutral">AI Resume Intelligence</span>
        <h1 style={{ marginTop: 16, fontSize: "2.4rem" }}>
          Know exactly why your resume scores the way it does.
        </h1>
        <p style={{ fontSize: "1.05rem", color: "var(--color-text-muted)" }}>
          Upload a resume, get an explainable ATS score, and see precisely which
          skills and keywords are missing for the job you want - no black-box
          scoring, every point is accounted for.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
          <Link to={isAuthenticated ? "/dashboard" : "/register"} className="btn btn-primary">
            {isAuthenticated ? "Go to dashboard" : "Get started"}
          </Link>
          {!isAuthenticated && (
            <Link to="/login" className="btn btn-secondary">
              Log in
            </Link>
          )}
        </div>
      </div>

      <div
        style={{
          marginTop: 56,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        <FeatureCard
          title="Explainable ATS score"
          body="Every point earned or lost is broken down into a concrete, human-readable factor."
        />
        <FeatureCard
          title="Job match analysis"
          body="Paste a job description and see your skill, keyword, and semantic match side by side."
        />
        <FeatureCard
          title="Built incrementally"
          body="Each phase of this platform ships independently, from parsing to AI-assisted optimization."
        />
      </div>
    </div>
  );
}

function FeatureCard({ title, body }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p style={{ margin: 0, color: "var(--color-text-muted)", fontSize: "0.9rem" }}>{body}</p>
    </div>
  );
}