import React, { useEffect, useState } from "react";
import { Copy, FileJson, FileText, Loader2 } from "lucide-react";
import { endpoints, fetchBlob } from "../api.js";
import { Alert, CardTitle } from "./ui.jsx";

/** Shows the real PDF/JSON the backend generates (fetched fresh, so it reflects extraction results). */
export default function ReportViewer({ id, analysis }) {
  const [tab, setTab] = useState("pdf");
  const [state, setState] = useState({ pdf: null, json: null, error: null, loading: false });
  const extStatus = analysis.extraction.status;

  useEffect(() => {
    let dead = false;
    let pdfUrl = null;
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.all([fetchBlob(endpoints.report(id)), fetchBlob(endpoints.json(id)).then((b) => b.text())])
      .then(([pdfBlob, jsonText]) => {
        if (dead) return;
        pdfUrl = URL.createObjectURL(pdfBlob);
        setState({ pdf: pdfUrl, json: jsonText, error: null, loading: false });
      })
      .catch((e) => !dead && setState({ pdf: null, json: null, error: e.message, loading: false }));
    return () => { dead = true; if (pdfUrl) URL.revokeObjectURL(pdfUrl); };
  }, [id, extStatus]);

  const Tab = ({ k, icon: Icon, children }) => (
    <button onClick={() => setTab(k)} className={`btn !py-1.5 ${tab === k ? "bg-emerald-600 text-white shadow-xs" : "text-slate-700 hover:bg-emerald-50"}`} aria-pressed={tab === k}>
      <Icon className="h-4 w-4" aria-hidden="true" /> {children}
    </button>
  );

  return (
    <div className="card">
      <CardTitle title="Forensic report viewer" icon={FileText}
        right={<div className="flex gap-1"><Tab k="pdf" icon={FileText}>PDF</Tab><Tab k="json" icon={FileJson}>JSON</Tab></div>} />
      {state.loading && <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin text-emerald-600" /> Generating report…</div>}
      {state.error && <Alert title="Could not load report">{state.error}</Alert>}
      {!state.loading && !state.error && tab === "pdf" && state.pdf && (
        <iframe title="Forensic PDF report" src={state.pdf} className="h-[640px] w-full rounded-lg border border-emerald-900/15 bg-white shadow-2xs" />
      )}
      {!state.loading && !state.error && tab === "json" && state.json && (
        <div className="relative">
          <button className="btn-ghost absolute right-2 top-2 !px-2.5 !py-1.5 text-xs shadow-xs" onClick={() => navigator.clipboard?.writeText(state.json)}><Copy className="h-3.5 w-3.5" aria-hidden="true" /> Copy</button>
          <pre className="max-h-[560px] overflow-auto rounded-lg border border-emerald-900/15 bg-emerald-950/5 p-4 font-mono text-xs text-emerald-950">{state.json}</pre>
        </div>
      )}
      <p className="mt-3 text-xs text-slate-500">The report regenerates after extraction so it includes the recovered-file details and thumbnail.</p>
    </div>
  );
}
