import React, { useCallback, useEffect, useState } from "react";
import { FlaskConical, ScanLine, ShieldCheck, Sparkles } from "lucide-react";
import * as api from "./api.js";
import Landing from "./components/Landing.jsx";
import UploadZone from "./components/UploadZone.jsx";
import Results from "./components/Results.jsx";
import DemoLab from "./components/DemoLab.jsx";
import ComicExplainer from "./components/ComicExplainer.jsx";
import { Alert, Badge } from "./components/ui.jsx";

export default function App() {
  const [view, setView] = useState("landing"); // landing | analyze | results | lab
  const [backend, setBackend] = useState({ state: "checking", info: null });
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState(null);
  const [pendingFile, setPendingFile] = useState(null);

  useEffect(() => {
    api.health().then((info) => setBackend({ state: "online", info })).catch(() => setBackend({ state: "offline", info: null }));
  }, []);

  const runAnalysis = useCallback(async (file) => {
    setBusy(true); setError(null); setProgress(0);
    try {
      const result = await api.analyze(file, setProgress);
      setAnalysis(result);
      setExtractError(null);
      setView("results");

      // Automatically decode / extract hidden image & payload
      try {
        setExtracting(true);
        const extracted = await api.extract(result.analysis_id);
        setAnalysis(extracted);
      } catch (err) {
        setExtractError(err.message);
      } finally {
        setExtracting(false);
      }
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }, []);

  const runExtraction = useCallback(async () => {
    if (!analysis) return;
    setExtracting(true); setExtractError(null);
    try {
      setAnalysis(await api.extract(analysis.analysis_id));
    } catch (e) {
      setExtractError(e.message);
    } finally {
      setExtracting(false);
    }
  }, [analysis]);

  const reset = () => { setAnalysis(null); setPendingFile(null); setError(null); setView("analyze"); };
  const fromLab = (file) => { setPendingFile(file); setError(null); setView("analyze"); };

  const nav = (v, label, Icon) => (
    <button onClick={() => setView(v)} aria-current={view === v ? "page" : undefined}
            className={`btn !py-1.5 ${view === v || (v === "analyze" && view === "results") ? "bg-emerald-600 text-white shadow-xs" : "text-slate-700 hover:bg-emerald-50 hover:text-emerald-900"}`}>
      <Icon className="h-4 w-4" aria-hidden="true" /> <span className="hidden sm:inline">{label}</span>
    </button>
  );

  return (
    <div className="min-h-screen bg-[#f7fbf8] text-slate-800">
      <header className="sticky top-0 z-20 border-b border-emerald-900/10 bg-white/90 backdrop-blur shadow-xs">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-6 py-3">
          <button className="flex items-center gap-2 text-left" onClick={() => setView("landing")} aria-label="StegoVision AI home">
            <ShieldCheck className="h-6 w-6 text-emerald-600" aria-hidden="true" />
            <span className="font-bold tracking-tight text-slate-900">StegoVision <span className="text-emerald-600">AI</span></span>
          </button>
          <nav className="flex items-center gap-1" aria-label="Main">
            {nav(analysis ? "results" : "analyze", "Analyze", ScanLine)}
            {nav("lab", "Test lab", FlaskConical)}
            {nav("comics", "Real-time comics", Sparkles)}
            <span className="ml-2 hidden md:inline-flex">
              {backend.state === "online" && <Badge tone="success">API online{backend.info?.ai_model_available ? " · AI model" : " · no AI model"}</Badge>}
              {backend.state === "offline" && <Badge tone="error">API offline</Badge>}
              {backend.state === "checking" && <Badge tone="muted">Checking API…</Badge>}
            </span>
          </nav>
        </div>
      </header>

      <main>
        {backend.state === "offline" && view !== "landing" && (
          <div className="mx-auto max-w-3xl px-6 pt-8">
            <Alert title="Backend unreachable">
              Start the FastAPI server (<code className="font-mono">uvicorn app.main:app</code> in <code className="font-mono">backend/</code>) or set
              <code className="font-mono"> VITE_API_BASE_URL</code> and the backend's <code className="font-mono">ALLOWED_ORIGINS</code>.
            </Alert>
          </div>
        )}
        {view === "landing" && (
          <Landing
            onStart={() => setView(analysis ? "results" : "analyze")}
            onLab={() => setView("lab")}
            onComics={() => setView("comics")}
          />
        )}
        {view === "comics" && <ComicExplainer onAnalyzeDemo={() => setView("lab")} />}
        {view === "analyze" && (
          <>
            <UploadZone key={pendingFile ? `${pendingFile.name}-${pendingFile.size}` : "empty"} onAnalyze={runAnalysis} busy={busy}
                        progress={progress} maxBytes={backend.info?.limits?.max_upload_bytes} initialFile={pendingFile} />
            {error && (
              <div className="mx-auto -mt-6 max-w-3xl px-6 pb-10">
                <Alert title={error.code === "unsupported_format" || error.code === "corrupted_image" ? "This file was rejected" : "Analysis failed"}>
                  {error.message} <span className="font-mono text-xs text-slate-500">[{error.code}]</span>
                </Alert>
              </div>
            )}
          </>
        )}
        {view === "results" && analysis && (
          <Results analysis={analysis} onExtract={runExtraction} extracting={extracting} extractError={extractError} onReset={reset} />
        )}
        {view === "results" && !analysis && <UploadZone onAnalyze={runAnalysis} busy={busy} progress={progress} />}
        {view === "lab" && <DemoLab onAnalyzeFile={fromLab} />}
      </main>

      <footer className="border-t border-emerald-900/10 bg-white/60 py-6 text-center text-xs text-slate-500">
        StegoVision AI · statistical forensics, not proof · custom-format extraction supports SVAI v1 only
      </footer>
    </div>
  );
}
