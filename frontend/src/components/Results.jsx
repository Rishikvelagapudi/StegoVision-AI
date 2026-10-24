import React, { useEffect, useState } from "react";
import {
  AlertTriangle, Binary, CheckCircle2, Cpu, Download, Eye, FileImage, FileJson, FileText, HelpCircle,
  Info, Layers, Loader2, RefreshCw, Search, ShieldAlert, ShieldCheck, XCircle, Fingerprint,
} from "lucide-react";
import { download, endpoints, fetchBlob } from "../api.js";
import { KIND_LABEL, OUTCOMES, SIGNAL_LABEL, TONES, formatBytes, shortHash } from "../utils.js";
import { Alert, Badge, CardTitle, KV, Stat } from "./ui.jsx";
import ReportViewer from "./ReportViewer.jsx";

function useBlobUrl(path, enabled = true) {
  const [s, setS] = useState({ url: null, error: null, loading: false });
  useEffect(() => {
    if (!enabled || !path) return undefined;
    let revoked = false;
    let objectUrl = null;
    setS({ url: null, error: null, loading: true });
    fetchBlob(path)
      .then((b) => {
        if (revoked) return;
        objectUrl = URL.createObjectURL(b);
        setS({ url: objectUrl, error: null, loading: false });
      })
      .catch((e) => !revoked && setS({ url: null, error: e.message, loading: false }));
    return () => { revoked = true; if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [path, enabled]);
  return s;
}

export default function Results({ analysis, onExtract, extracting, extractError, onReset }) {
  const id = analysis.analysis_id;
  const det = analysis.detection;
  const ext = analysis.extraction;
  const [dlError, setDlError] = useState(null);
  const safeDownload = async (path, name) => {
    setDlError(null);
    try { await download(path, name); } catch (e) { setDlError(e.message); }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-6 py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="truncate text-2xl font-extrabold text-slate-900" title={analysis.filename}>{analysis.filename}</h2>
          <p className="mt-1 font-mono text-xs text-slate-500">
            ID {id.slice(0, 8)} · SHA-256 {shortHash(analysis.sha256)} · {new Date(analysis.timestamp).toLocaleString()} · {analysis.duration_ms} ms
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-ghost" onClick={() => safeDownload(endpoints.report(id), `stegovision_report_${id.slice(0, 8)}.pdf`)}><FileText className="h-4 w-4" aria-hidden="true" /> PDF report</button>
          <button className="btn-ghost" onClick={() => safeDownload(endpoints.json(id), `stegovision_analysis_${id.slice(0, 8)}.json`)}><FileJson className="h-4 w-4" aria-hidden="true" /> JSON</button>
          <button className="btn-primary" onClick={onReset}><RefreshCw className="h-4 w-4" aria-hidden="true" /> New analysis</button>
        </div>
      </div>
      {dlError && <Alert title="Download failed">{dlError}</Alert>}

      <DetectionBanner det={det} />

      <div className="grid gap-4 lg:grid-cols-2">
        <OriginalPanel analysis={analysis} />
        <RecoveredPanel analysis={analysis} onExtract={onExtract} extracting={extracting} extractError={extractError}
                        onDownload={() => safeDownload(endpoints.recovered(id), ext.recovered?.filename || "recovered")} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <MetadataCard meta={analysis.metadata} />
        <StatisticsCard stats={analysis.statistics} />
        <LsbCard lsb={analysis.lsb} />
        <div className="space-y-4">
          <AiCard ai={det.ai} />
          <ExtractionCard ext={ext} />
        </div>
      </div>

      <LsbVisualization id={id} />
      <ReportViewer id={id} analysis={analysis} />

      <div className="card">
        <CardTitle icon={Info} title="Limitations of this analysis" />
        <ul className="list-disc space-y-1.5 pl-5 text-sm text-slate-600">
          {analysis.limitations.map((l) => <li key={l}>{l}</li>)}
        </ul>
      </div>
    </div>
  );
}

function DetectionBanner({ det }) {
  const meta = OUTCOMES[det.outcome] || OUTCOMES.Inconclusive;
  const t = TONES[meta.tone];
  const Icon = meta.tone === "warning" ? ShieldAlert : meta.tone === "success" ? ShieldCheck : HelpCircle;
  return (
    <section className={`rounded-2xl border p-6 shadow-xs animate-fade-up ${t.border} ${t.bg}`} aria-label="Detection result">
      <div className="flex flex-wrap items-center gap-4">
        <Icon className={`h-10 w-10 ${t.text}`} aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <div className="label">Detection status</div>
          <div className={`text-2xl font-bold ${t.text}`}>{det.outcome}</div>
          <p className="mt-1 text-sm text-slate-700">{det.explanation}</p>
        </div>
      </div>
      <div className="mt-5 grid gap-2 md:grid-cols-2">
        {det.detectors.map((d) => {
          const [label, tone] = SIGNAL_LABEL[d.signal] || ["—", "muted"];
          return (
            <div key={d.name} className="rounded-lg border border-emerald-900/10 bg-white/90 p-3 shadow-2xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-mono text-xs font-semibold text-slate-800">{d.name}</span>
                <span className="flex gap-1.5">
                  <Badge tone="muted">{KIND_LABEL[d.kind] || d.kind}</Badge>
                  <Badge tone={tone}>{label}</Badge>
                </span>
              </div>
              <p className="mt-1.5 text-xs text-slate-600">{d.summary}</p>
            </div>
          );
        })}
      </div>
      <p className="mt-4 text-xs text-slate-500">
        Detection never proves steganography and does not decode anything. Extraction is a separate step below.
      </p>
    </section>
  );
}

function OriginalPanel({ analysis }) {
  const { url, error, loading } = useBlobUrl(endpoints.original(analysis.analysis_id));
  const im = analysis.image;
  return (
    <div className="card">
      <CardTitle icon={FileImage} title="Original upload" right={<Badge tone="muted">{im.format}</Badge>} />
      <div className="flex min-h-[220px] items-center justify-center rounded-lg border border-emerald-900/10 bg-emerald-50/40 p-2">
        {loading && <Loader2 className="h-6 w-6 animate-spin text-slate-400" aria-label="Loading image" />}
        {error && <span className="text-sm text-rose-700">{error}</span>}
        {url && <img src={url} alt="Original upload" className="max-h-80 max-w-full rounded object-contain shadow-2xs" />}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Dimensions" value={`${im.width} × ${im.height}`} />
        <Stat label="File size" value={formatBytes(analysis.file_size_bytes)} />
        <Stat label="Format" value={`${im.format} / ${im.mode}`} />
        <Stat label="LSB capacity" value={formatBytes(im.lsb_capacity_bytes)} />
      </div>
    </div>
  );
}

function RecoveredPanel({ analysis, onExtract, extracting, extractError, onDownload }) {
  const ext = analysis.extraction;
  const rec = ext.recovered;
  const showImage = ext.status === "success" && rec?.kind === "image";
  const { url, error, loading } = useBlobUrl(endpoints.recovered(analysis.analysis_id), showImage);
  const status = extracting ? ["Running", "neutral"] : ext.status === "success" ? ["Recovered", "success"]
    : ext.status === "failed" ? ["Failed", "error"] : ["Not attempted", "muted"];

  return (
    <div className="card">
      <CardTitle icon={Binary} title="Decoded image &amp; payload" right={<Badge tone={status[1]}>{status[0]}</Badge>} />
      <div className="flex min-h-[220px] items-center justify-center rounded-lg border border-emerald-900/10 bg-emerald-50/40 p-3">
        {extracting && <div className="text-center text-sm text-slate-600"><Loader2 className="mx-auto mb-2 h-6 w-6 animate-spin text-emerald-600" />Decoding and extracting hidden image/payload…</div>}
        {!extracting && ext.status === "not_attempted" && (
          <div className="text-center">
            <p className="mx-auto mb-4 max-w-xs text-sm text-slate-600">Click to decode any hidden images or payloads using supported LSB and trailer extraction methods.</p>
            <button className="btn-primary" onClick={onExtract}><Search className="h-4 w-4" aria-hidden="true" /> Decode Image / Payload</button>
          </div>
        )}
        {!extracting && ext.status === "failed" && (
          <div className="w-full text-sm">
            <div className="mb-2 flex items-center gap-2 font-medium text-rose-800"><XCircle className="h-4 w-4 text-rose-600" aria-hidden="true" /> Extraction did not recover a supported payload</div>
            <p className="mb-1 text-slate-600">Possible reasons:</p>
            <ul className="list-disc space-y-1 pl-5 text-xs text-slate-600">{ext.possible_reasons.map((r) => <li key={r}>{r}</li>)}</ul>
            <button className="btn-ghost mt-4" onClick={onExtract}><RefreshCw className="h-4 w-4" aria-hidden="true" /> Retry decoding</button>
          </div>
        )}
        {!extracting && showImage && (
          <div className="flex flex-col items-center gap-2 w-full">
            {loading && <Loader2 className="h-6 w-6 animate-spin text-slate-400" aria-label="Loading recovered image" />}
            {error && <span className="text-sm text-rose-700">{error}</span>}
            {url && (
              <>
                <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100/90 border border-emerald-300 px-3 py-1 text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" /> Decoded image verified from content
                </div>
                <img src={url} alt="Recovered hidden image" className="pixelated max-h-80 max-w-full rounded border border-emerald-900/15 object-contain shadow-xs bg-white p-1" style={{ minWidth: 96 }} />
              </>
            )}
          </div>
        )}
        {!extracting && ext.status === "success" && rec?.kind === "text" && (
          <pre className="max-h-72 w-full overflow-auto whitespace-pre-wrap break-words rounded bg-emerald-950/5 border border-emerald-900/10 p-3 font-mono text-sm text-emerald-950 font-medium">{rec.text_preview}{rec.truncated ? "\n… (truncated — download for full text)" : ""}</pre>
        )}
      </div>
      {extractError && <div className="mt-3"><Alert title="Extraction request failed">{extractError}</Alert></div>}
      {ext.status === "success" && rec && (
        <>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Filename" value={rec.filename} mono />
            <Stat label="Format" value={rec.format} />
            <Stat label="Size" value={formatBytes(rec.size_bytes)} />
            <Stat label={rec.kind === "image" ? "Dimensions" : "Characters"} value={rec.kind === "image" ? `${rec.width} × ${rec.height}` : rec.char_count} />
          </div>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <span className="flex items-center gap-1.5 text-xs text-slate-600"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" /> Validated from content · method {rec.method} · SHA-256 {shortHash(rec.sha256)}</span>
            <button className="btn-primary" onClick={onDownload}><Download className="h-4 w-4" aria-hidden="true" /> Download</button>
          </div>
        </>
      )}
    </div>
  );
}

function MetadataCard({ meta }) {
  const m = meta.measured;
  return (
    <div className="card">
      <CardTitle icon={Layers} title="Metadata analysis" right={<Badge tone="muted">Measured</Badge>} />
      <KV rows={[
        ["EXIF fields", m.exif_field_count], ["Text fields", Object.keys(m.text_fields || {}).length],
        ["ICC profile", m.has_icc_profile ? "yes" : "no"],
        ["Trailing data", `${m.trailing_data_bytes || 0} bytes${m.trailing_data_type ? ` (${m.trailing_data_type})` : ""}`],
        ...(m.png_chunk_count ? [["PNG chunks", m.png_chunk_count]] : []),
      ]} />
      <ul className="mt-3 space-y-2">
        {meta.observations.map((o, i) => (
          <li key={i} className="flex gap-2 text-xs text-slate-600">
            {o.severity === "notable" ? <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" aria-hidden="true" /> : <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" aria-hidden="true" />}
            <span>{o.message}</span>
          </li>
        ))}
      </ul>
      {Object.keys(m.exif || {}).length > 0 && (
        <details className="mt-3 text-xs text-slate-600"><summary className="cursor-pointer font-medium text-emerald-800 hover:text-emerald-900">EXIF values</summary>
          <KV rows={Object.entries(m.exif).slice(0, 20)} /></details>
      )}
    </div>
  );
}

function Histogram({ data }) {
  const max = Math.max(...data, 1);
  return (
    <svg viewBox="0 0 256 60" className="h-16 w-full" role="img" aria-label="Grayscale histogram" preserveAspectRatio="none">
      {data.map((v, i) => <rect key={i} x={i} y={60 - (v / max) * 58} width="1" height={(v / max) * 58} className="fill-emerald-600/80" />)}
    </svg>
  );
}

function StatisticsCard({ stats }) {
  const m = stats.measured;
  return (
    <div className="card">
      <CardTitle icon={Cpu} title="Statistical analysis" right={<Badge tone="muted">Measured</Badge>} />
      <div className="mb-3 grid grid-cols-2 gap-3">
        <Stat label="Gray entropy" value={`${m.grayscale_entropy_bits} / 8 bits`} />
        <Stat label="Laplacian var." value={m.laplacian_variance} />
        <Stat label="Unique gray levels" value={m.unique_gray_levels} />
        <Stat label="Saturated pixels" value={`${(m.saturated_pixel_fraction * 100).toFixed(2)}%`} />
      </div>
      <Histogram data={m.histogram_gray} />
      <table className="mt-3 w-full text-xs">
        <thead><tr className="text-left font-semibold text-emerald-950/70"><th className="py-1">Channel</th><th>Entropy</th><th>Unique</th><th>Adj. corr.</th></tr></thead>
        <tbody className="font-mono text-slate-800">
          {Object.entries(m.channels).map(([c, v]) => (
            <tr key={c} className="border-t border-emerald-900/10"><td className="py-1 capitalize font-sans">{c}</td><td>{v.entropy_bits}</td><td>{v.unique_values}</td><td>{v.adjacent_pixel_correlation}</td></tr>
          ))}
        </tbody>
      </table>
      <ul className="mt-3 space-y-1 text-xs text-slate-600">
        {stats.interpretation.map((s) => <li key={s}><Badge tone="muted" className="mr-1.5">Heuristic</Badge>{s}</li>)}
      </ul>
    </div>
  );
}

function LsbCard({ lsb }) {
  const probe = lsb.custom_header_probe;
  const rs = lsb.rs_analysis;
  return (
    <div className="card">
      <CardTitle icon={Fingerprint} title="LSB findings" right={<span className="flex gap-1.5"><Badge tone="muted">Measured</Badge><Badge tone="muted">Heuristic</Badge></span>} />
      <table className="w-full text-xs">
        <thead><tr className="text-left font-semibold text-emerald-950/70"><th className="py-1">Plane</th><th>Ones ratio</th><th>Bit entropy</th><th>Horiz. agree</th></tr></thead>
        <tbody className="font-mono text-slate-800">
          {Object.entries(lsb.bit_statistics).map(([c, v]) => (
            <tr key={c} className="border-t border-emerald-900/10"><td className="py-1 capitalize font-sans">{c}</td><td>{v.ones_ratio}</td><td>{v.bit_entropy}</td><td>{v.horizontal_agreement}</td></tr>
          ))}
        </tbody>
      </table>
      <div className="label mt-4">Chi-square (pairs of values) — p near 1 = pairs equalised</div>
      <table className="mt-1 w-full text-xs">
        <tbody className="font-mono text-slate-800">
          {lsb.chi_square_windows.map((w) => (
            <tr key={w.samples} className="border-t border-emerald-900/10">
              <td className="py-1 font-sans">{w.samples.toLocaleString()} samples</td>
              <td className="text-right">{w.valid ? `p = ${w.p_value}` : <span className="text-slate-400 font-sans">n/a</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="label mt-4">RS analysis — estimated modified fraction of LSB capacity</div>
      <div className="mt-1 font-mono text-sm font-semibold text-slate-900">
        {rs.valid ? `${(rs.mean_estimated_payload_fraction * 100).toFixed(1)}%` : "not available"}
        {rs.valid && <span className="ml-2 text-xs font-normal text-slate-500">({Object.entries(rs.channels).map(([c, v]) => `${c[0].toUpperCase()}: ${v.valid ? (v.estimated_payload_fraction * 100).toFixed(1) + "%" : "n/a"}`).join(", ")})</span>}
      </div>
      <div className="label mt-4">StegoVision (SVAI) header probe</div>
      <div className="mt-1 text-sm">
        {probe.signature_found
          ? <span className="font-semibold text-amber-800">Signature found · v{probe.version} · type {probe.type_id} · {probe.length} bytes</span>
          : <span className="text-slate-600">No SVAI signature in LSBs (says nothing about other methods)</span>}
      </div>
    </div>
  );
}

function AiCard({ ai }) {
  return (
    <div className="card">
      <CardTitle icon={Cpu} title="AI classification" right={<Badge tone="muted">Model</Badge>} />
      {ai.available ? (
        <KV rows={[["Prediction", ai.prediction], ["Confidence", ai.confidence], ["Patches evaluated", ai.patches_evaluated]]} />
      ) : (
        <>
          <KV rows={[["Status", "Not available"], ["Prediction", "Not Available"], ["Confidence", "Not Available"]]} />
          <p className="mt-2 text-xs text-slate-500">{ai.reason}</p>
        </>
      )}
    </div>
  );
}

function ExtractionCard({ ext }) {
  return (
    <div className="card">
      <CardTitle icon={Binary} title="Extraction methods" right={<Badge tone={ext.status === "success" ? "success" : ext.status === "failed" ? "error" : "muted"}>{ext.status.replace("_", " ")}</Badge>} />
      {ext.methods_attempted.length === 0 ? (
        <p className="text-xs text-slate-500">Not attempted yet. Detection and extraction are separate operations.</p>
      ) : (
        <ul className="space-y-2">
          {ext.methods_attempted.map((m) => (
            <li key={m.method} className="rounded-lg border border-emerald-900/10 bg-emerald-50/40 p-2.5 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono font-semibold text-slate-900">{m.method}</span>
                <Badge tone={m.status === "success" ? "success" : "error"}>{m.status}</Badge>
              </div>
              <p className="mt-1 text-slate-600">{m.message}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function LsbVisualization({ id }) {
  const { url, error, loading } = useBlobUrl(endpoints.lsb(id));
  return (
    <div className="card border-dashed border-emerald-400/50 bg-white">
      <CardTitle icon={Eye} title="LSB bit-plane visualization" right={<Badge tone="neutral">Forensic view · not a recovered image</Badge>} />
      <p className="mb-3 text-sm text-slate-600">
        Each colour channel's least-significant bit mapped to 0 or 255. Structured regions suggest natural image content;
        uniform noise over a region may indicate overwritten LSBs. This is a diagnostic picture of the bit-plane — it is
        <strong className="font-semibold text-slate-900"> not</strong> a decoded hidden image.
      </p>
      <div className="flex min-h-[160px] items-center justify-center overflow-hidden rounded-lg border border-emerald-900/10 bg-emerald-50/40 p-2">
        {loading && <Loader2 className="h-6 w-6 animate-spin text-slate-400" aria-label="Loading visualization" />}
        {error && <span className="text-sm text-rose-700">{error}</span>}
        {url && <img src={url} alt="LSB bit-plane visualization (forensic view, not a recovered image)" className="pixelated max-h-96 max-w-full object-contain shadow-2xs" />}
      </div>
    </div>
  );
}
