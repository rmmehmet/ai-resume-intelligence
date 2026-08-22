function Chips({ items, tone }) {
  if (!items.length) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
      {items.map((item) => (
        <span key={item} className={`badge badge-${tone}`}>
          {item}
        </span>
      ))}
    </div>
  );
}

/**
 * Shows the job-specific keyword/skill scan from an ATS analysis -
 * the part that mirrors how a real ATS screens a resume against a
 * specific requisition, as opposed to the generic parseability score.
 */
export default function JobMatchPanel({ jobMatch }) {
  return (
    <div
      style={{
        marginTop: 20,
        paddingTop: 20,
        borderTop: "1px solid var(--color-border)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ margin: 0 }}>Match for "{jobMatch.job_title}"</h3>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontWeight: 600,
            fontSize: "1.1rem",
          }}
        >
          {Math.round(jobMatch.match_score)}%
        </span>
      </div>

      <div style={{ marginTop: 12, display: "grid", gap: 16, gridTemplateColumns: "1fr 1fr" }}>
        <div>
          <h4 style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", margin: 0 }}>
            Matched skills
          </h4>
          <Chips items={jobMatch.matched_skills} tone="good" />
        </div>
        <div>
          <h4 style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", margin: 0 }}>
            Missing skills
          </h4>
          <Chips items={jobMatch.missing_skills} tone="low" />
        </div>
        <div>
          <h4 style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", margin: 0 }}>
            Matched keywords
          </h4>
          <Chips items={jobMatch.matched_keywords} tone="good" />
        </div>
        <div>
          <h4 style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", margin: 0 }}>
            Missing keywords
          </h4>
          <Chips items={jobMatch.missing_keywords} tone="low" />
        </div>
      </div>
    </div>
  );
}