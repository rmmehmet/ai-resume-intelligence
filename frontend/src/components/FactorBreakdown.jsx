export default function FactorBreakdown({ factors }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {factors.map((factor) => {
        const pct = factor.points_possible
          ? Math.round((factor.points_earned / factor.points_possible) * 100)
          : 0;
        return (
          <div key={factor.key}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: 4,
              }}
            >
              <span style={{ fontWeight: 600, fontSize: "0.88rem" }}>{factor.label}</span>
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.8rem",
                  color: "var(--color-text-muted)",
                }}
              >
                {factor.points_earned}/{factor.points_possible}
              </span>
            </div>
            <div
              style={{
                height: 6,
                borderRadius: 999,
                background: "var(--color-border)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${pct}%`,
                  height: "100%",
                  background: factor.passed ? "var(--color-good)" : "var(--color-mid)",
                  transition: "width 0.3s ease",
                }}
              />
            </div>
            <p style={{ margin: "6px 0 0", fontSize: "0.82rem", color: "var(--color-text-muted)" }}>
              {factor.explanation}
            </p>
          </div>
        );
      })}
    </div>
  );
}