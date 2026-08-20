import ScoreRing from "./ScoreRing";

function KeywordChips({ items, tone }) {
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

export default function MatchResultCard({ result }) {
  return (
    <div className="card">
      <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
        <ScoreRing score={result.overall_score} label="Overall match" />
        <div style={{ display: "flex", gap: 20 }}>
          <MiniScore label="Skills" value={result.skill_score} />
          <MiniScore label="Keywords" value={result.keyword_score} />
          <MiniScore label="Semantic" value={result.semantic_score} />
        </div>
      </div>

      <div style={{ marginTop: 20, display: "grid", gap: 16, gridTemplateColumns: "1fr 1fr" }}>
        <div>
          <h3 style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>Matched skills</h3>
          <KeywordChips items={result.matched_skills} tone="good" />
        </div>
        <div>
          <h3 style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>Missing skills</h3>
          <KeywordChips items={result.missing_skills} tone="low" />
        </div>
        <div>
          <h3 style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>Matched keywords</h3>
          <KeywordChips items={result.matched_keywords} tone="good" />
        </div>
        <div>
          <h3 style={{ fontSize: "0.85rem", color: "var(--color-text-muted)" }}>Missing keywords</h3>
          <KeywordChips items={result.missing_keywords} tone="low" />
        </div>
      </div>
    </div>
  );
}

function MiniScore({ label, value }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.3rem", fontWeight: 600 }}>
        {Math.round(value)}
      </div>
      <div style={{ fontSize: "0.72rem", color: "var(--color-text-muted)" }}>{label}</div>
    </div>
  );
}