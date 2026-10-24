import React from "react";
import { TONES } from "../utils.js";

export function Badge({ tone = "muted", children, className = "" }) {
  const t = TONES[tone] || TONES.muted;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${t.border} ${t.bg} ${t.text} ${className}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${t.dot}`} />
      {children}
    </span>
  );
}

export function Stat({ label, value, mono = false }) {
  return (
    <div className="min-w-0">
      <div className="label">{label}</div>
      <div className={`mt-0.5 truncate text-sm font-semibold text-slate-900 ${mono ? "font-mono" : ""}`} title={String(value ?? "")}>
        {value ?? "—"}
      </div>
    </div>
  );
}

export function CardTitle({ icon: Icon, title, right }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900">
        {Icon && <Icon className="h-4 w-4 text-emerald-600" aria-hidden="true" />}
        {title}
      </h3>
      {right}
    </div>
  );
}

export function Alert({ tone = "error", title, children }) {
  const t = TONES[tone];
  return (
    <div role="alert" className={`rounded-lg border p-4 text-sm ${t.border} ${t.bg}`}>
      {title && <div className={`mb-1 font-semibold ${t.text}`}>{title}</div>}
      <div className="text-slate-700">{children}</div>
    </div>
  );
}

export function KV({ rows }) {
  return (
    <dl className="divide-y divide-emerald-900/10 text-sm">
      {rows.map(([k, v]) => (
        <div key={k} className="flex justify-between gap-4 py-1.5">
          <dt className="text-slate-600">{k}</dt>
          <dd className="text-right font-mono font-medium text-slate-900 break-all">{v ?? "—"}</dd>
        </div>
      ))}
    </dl>
  );
}
