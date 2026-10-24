import React, { useCallback, useEffect, useRef, useState } from "react";
import { FileImage, Loader2, ScanLine, Trash2, Upload } from "lucide-react";
import { formatBytes } from "../utils.js";
import { Alert } from "./ui.jsx";

const ACCEPT = ["image/png", "image/jpeg", "image/bmp"];

export default function UploadZone({ onAnalyze, busy, progress, maxBytes, initialFile }) {
  const [file, setFile] = useState(initialFile || null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!file) return setPreview(null);
    const u = URL.createObjectURL(file);
    setPreview(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);

  const pick = useCallback((f) => {
    setError(null);
    if (!f) return;
    if (!ACCEPT.includes(f.type) && !/\.(png|jpe?g|bmp)$/i.test(f.name)) {
      return setError("Please choose a PNG, JPEG or BMP image. (The server also verifies the real file contents.)");
    }
    if (maxBytes && f.size > maxBytes) return setError(`File is ${formatBytes(f.size)}; the limit is ${formatBytes(maxBytes)}.`);
    setFile(f);
  }, [maxBytes]);

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h2 className="text-2xl font-extrabold text-slate-900">Analyze &amp; Decode image</h2>
      <p className="mt-1 text-sm text-slate-600">Supported: PNG, JPEG, BMP. Runs forensics and automatically extracts &amp; decodes hidden images and payloads.</p>

      <div
        role="button"
        tabIndex={0}
        aria-label="Upload image: drag and drop or press Enter to browse"
        onClick={() => !busy && inputRef.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && !busy && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); !busy && pick(e.dataTransfer.files?.[0]); }}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition
          ${dragging ? "border-emerald-500 bg-emerald-50" : "border-emerald-300/80 bg-white hover:border-emerald-500 hover:bg-emerald-50/30 shadow-xs"} ${busy ? "pointer-events-none opacity-60" : ""}`}
      >
        <input ref={inputRef} type="file" accept=".png,.jpg,.jpeg,.bmp,image/png,image/jpeg,image/bmp" className="hidden"
               onChange={(e) => { pick(e.target.files?.[0]); e.target.value = ""; }} />
        {preview ? (
          <img src={preview} alt="Selected upload preview" className="max-h-64 rounded-lg border border-emerald-900/10 object-contain" />
        ) : (
          <>
            <Upload className="h-10 w-10 text-emerald-600" aria-hidden="true" />
            <p className="mt-3 font-semibold text-slate-900">Drag &amp; drop an image here</p>
            <p className="text-sm text-slate-500">or click to browse{maxBytes ? ` · max ${formatBytes(maxBytes)}` : ""}</p>
          </>
        )}
      </div>

      {error && <div className="mt-4"><Alert title="Cannot use this file">{error}</Alert></div>}

      {file && (
        <div className="card mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <FileImage className="h-5 w-5 shrink-0 text-emerald-600" aria-hidden="true" />
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold text-slate-900">{file.name}</div>
              <div className="text-xs text-slate-500">{formatBytes(file.size)} · {file.type || "unknown type"}</div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn-ghost" disabled={busy} onClick={() => { setFile(null); setError(null); }}><Trash2 className="h-4 w-4" aria-hidden="true" /> Clear</button>
            <button className="btn-primary" disabled={busy} onClick={() => onAnalyze(file)}>
              {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <ScanLine className="h-4 w-4" aria-hidden="true" />}
              {busy ? "Analyzing & Decoding…" : "Analyze & Decode image"}
            </button>
          </div>
        </div>
      )}

      {busy && <Progress progress={progress} />}
    </div>
  );
}

function Progress({ progress }) {
  const uploading = progress < 1;
  return (
    <div className="card mt-4" role="status" aria-live="polite">
      <div className="mb-2 flex justify-between text-sm">
        <span className="font-medium text-slate-800">{uploading ? "Uploading to backend" : "Server analysis in progress"}</span>
        <span className="font-mono text-slate-500">{uploading ? `${Math.round(progress * 100)}%` : "working…"}</span>
      </div>
      <div className="relative h-2 overflow-hidden rounded-full bg-emerald-100">
        {uploading ? (
          <div className="h-full bg-emerald-500 transition-all" style={{ width: `${Math.round(progress * 100)}%` }} />
        ) : (
          <div className="absolute inset-y-0 w-1/3 animate-sweep rounded-full bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
        )}
      </div>
      <p className="mt-2 text-xs text-slate-500">Validation → metadata → statistics → LSB analysis → detection pipeline</p>
    </div>
  );
}
