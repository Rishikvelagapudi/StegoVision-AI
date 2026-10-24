export function formatBytes(n) {
  if (n == null || Number.isNaN(n)) return "—";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

export const shortHash = (h) => (h ? `${h.slice(0, 12)}…${h.slice(-8)}` : "—");

export const OUTCOMES = {
  "Possible Steganography Detected": { tone: "warning", label: "Possible Steganography Detected" },
  "No Strong Evidence Detected": { tone: "success", label: "No Strong Evidence Detected" },
  Inconclusive: { tone: "neutral", label: "Inconclusive" },
};

export const TONES = {
  warning: { text: "text-amber-800", border: "border-amber-300", bg: "bg-amber-50", dot: "bg-amber-500" },
  success: { text: "text-emerald-800", border: "border-emerald-300", bg: "bg-emerald-50", dot: "bg-emerald-600" },
  neutral: { text: "text-emerald-800", border: "border-emerald-200", bg: "bg-emerald-50/70", dot: "bg-emerald-500" },
  error: { text: "text-rose-800", border: "border-rose-300", bg: "bg-rose-50", dot: "bg-rose-500" },
  muted: { text: "text-emerald-950/80", border: "border-emerald-900/15", bg: "bg-emerald-50/50", dot: "bg-emerald-600" },
};

export const SIGNAL_LABEL = {
  strong_for: ["Strong indicator", "warning"],
  for: ["Weak indicator", "warning"],
  neutral: ["Neutral", "muted"],
  against: ["Argues against", "success"],
  not_applicable: ["Not applicable", "muted"],
};

export const KIND_LABEL = { measured: "Measured", heuristic: "Heuristic", model: "Model" };
