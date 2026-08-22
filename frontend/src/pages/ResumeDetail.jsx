import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getResume } from "../services/resumeService";
import { analyzeResume, listAtsScores } from "../services/atsService";
import { createJob, listJobs } from "../services/jobService";
import { createMatch } from "../services/matchingService";
import ScoreRing from "../components/ScoreRing";
import FactorBreakdown from "../components/FactorBreakdown";
import JobMatchPanel from "../components/JobMatchPanel";
import MatchResultCard from "../components/MatchResultCard";

export default function ResumeDetail() {
  const { resumeId } = useParams();

  const [resume, setResume] = useState(null);

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [showJobForm, setShowJobForm] = useState(false);
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [isSavingJob, setIsSavingJob] = useState(false);
  const [jobError, setJobError] = useState("");

  const [latestScore, setLatestScore] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [atsError, setAtsError] = useState("");

  const [matchResult, setMatchResult] = useState(null);
  const [isMatching, setIsMatching] = useState(false);
  const [matchError, setMatchError] = useState("");

  useEffect(() => {
    loadResume();
    loadJobs();
    loadLatestScore();
  }, [resumeId]);

  async function loadResume() {
    try {
      const data = await getResume(resumeId);
      setResume(data);
    } catch {
      setAtsError("Couldn't load this resume.");
    }
  }

  async function loadLatestScore() {
    try {
      const scores = await listAtsScores(resumeId);
      if (scores.length > 0) setLatestScore(scores[0]);
    } catch {
      // No scores yet - not an error state worth surfacing.
    }
  }

  async function loadJobs() {
    try {
      const data = await listJobs();
      setJobs(data);
    } catch {
      // Job list is optional context here; fail silently.
    }
  }

  async function handleSaveJob(e) {
    e.preventDefault();
    setJobError("");
    setIsSavingJob(true);
    try {
      const job = await createJob({ title: jobTitle, description: jobDescription });
      setJobs((prev) => [{ id: job.id, title: job.title, created_at: job.created_at }, ...prev]);
      setSelectedJobId(String(job.id));
      setShowJobForm(false);
      setJobTitle("");
      setJobDescription("");
    } catch (err) {
      setJobError(err.response?.data?.detail || "Couldn't save this job description.");
    } finally {
      setIsSavingJob(false);
    }
  }

  async function handleAnalyze() {
    setAtsError("");
    setIsAnalyzing(true);
    try {
      const score = await analyzeResume(resumeId, selectedJobId || undefined);
      setLatestScore(score);
    } catch (err) {
      setAtsError(err.response?.data?.detail || "Couldn't run ATS analysis.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleMatch() {
    if (!selectedJobId) return;
    setMatchError("");
    setIsMatching(true);
    try {
      const result = await createMatch(resumeId, selectedJobId);
      setMatchResult(result);
    } catch (err) {
      setMatchError(err.response?.data?.detail || "Couldn't run job matching.");
    } finally {
      setIsMatching(false);
    }
  }

  if (!resume) {
    return <div className="container" style={{ paddingTop: 48 }}>Loading...</div>;
  }

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 64 }}>
      <Link to="/dashboard" style={{ fontSize: "0.85rem" }}>
        ← Back to resumes
      </Link>
      <h1 style={{ marginTop: 12 }}>{resume.original_filename}</h1>

      {/* Job selector - shared by ATS job-specific scan and full matching below */}
      <section className="card" style={{ marginTop: 24 }}>
        <h2>Job to check against (optional)</h2>
        <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
          Pick a saved job description, or paste a new one. Leave unselected for a
          general ATS parseability check.
        </p>

        <div style={{ marginTop: 16, display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{
              padding: "10px 12px",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--color-border)",
              minWidth: 220,
            }}
          >
            <option value="">No specific job</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>

          <button className="btn btn-secondary" onClick={() => setShowJobForm((s) => !s)}>
            {showJobForm ? "Cancel" : "+ New job description"}
          </button>
        </div>

        {showJobForm && (
          <form onSubmit={handleSaveJob} style={{ marginTop: 20, borderTop: "1px solid var(--color-border)", paddingTop: 20 }}>
            <div className="field">
              <label htmlFor="jobTitle">Job title</label>
              <input
                id="jobTitle"
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="jobDescription">Job description</label>
              <textarea
                id="jobDescription"
                required
                minLength={20}
                rows={8}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job description here..."
              />
            </div>
            {jobError && <p className="error-text">{jobError}</p>}
            <button type="submit" className="btn btn-primary" disabled={isSavingJob}>
              {isSavingJob ? "Saving..." : "Save job description"}
            </button>
          </form>
        )}
      </section>

      {/* ATS Analysis */}
      <section className="card" style={{ marginTop: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <div>
            <h2>ATS score</h2>
            <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
              Parseability and quality checks, based on how real ATS systems actually
              read a resume - plus a keyword/skill scan if a job is selected above.
            </p>
          </div>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? "Analyzing..." : latestScore ? "Re-analyze" : "Run ATS analysis"}
          </button>
        </div>

        {atsError && <p className="error-text">{atsError}</p>}

        {latestScore && (
          <>
            <div style={{ marginTop: 24, display: "flex", gap: 32, flexWrap: "wrap" }}>
              <ScoreRing score={latestScore.overall_score} label="ATS score" />
              <div style={{ flex: 1, minWidth: 260 }}>
                <FactorBreakdown factors={latestScore.factors} />
              </div>
            </div>

            {latestScore.job_match && <JobMatchPanel jobMatch={latestScore.job_match} />}
          </>
        )}
      </section>

      {/* Full semantic + keyword + skill match (Phase 5 engine) */}
      <section className="card" style={{ marginTop: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <div>
            <h2>Full match analysis</h2>
            <p style={{ color: "var(--color-text-muted)", margin: 0 }}>
              Skill, keyword, and semantic (sentence-embedding) similarity against the
              selected job.
            </p>
          </div>
          <button className="btn btn-primary" onClick={handleMatch} disabled={!selectedJobId || isMatching}>
            {isMatching ? "Matching..." : "Run match"}
          </button>
        </div>

        {matchError && <p className="error-text" style={{ marginTop: 16 }}>{matchError}</p>}
        {!selectedJobId && (
          <p style={{ marginTop: 16, fontSize: "0.85rem", color: "var(--color-text-muted)" }}>
            Select a job above to enable this.
          </p>
        )}
      </section>

      {matchResult && (
        <div style={{ marginTop: 20 }}>
          <MatchResultCard result={matchResult} />
        </div>
      )}
    </div>
  );
}