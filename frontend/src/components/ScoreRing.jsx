const SIZE = 88;
const STROKE = 8;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function tone(score) {
  if (score >= 70) return "good";
  if (score >= 40) return "mid";
  return "low";
}

const TONE_COLOR = {
  good: "var(--color-good)",
  mid: "var(--color-mid)",
  low: "var(--color-low)",
};

/**
 * Circular score indicator - the app's signature visual element.
 * Used anywhere a 0-100 score needs to be shown (ATS score, match score).
 */
export default function ScoreRing({ score, label }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const offset = CIRCUMFERENCE * (1 - clamped / 100);
  const color = TONE_COLOR[tone(clamped)];

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={STROKE}
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
          style={{ transition: "stroke-dashoffset 0.4s ease" }}
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          fontFamily="var(--font-mono)"
          fontSize="20"
          fontWeight="600"
          fill="var(--color-text)"
        >
          {Math.round(clamped)}
        </text>
      </svg>
      {label && (
        <span style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", fontWeight: 600 }}>
          {label}
        </span>
      )}
    </div>
  );
}