import React, { useEffect, useState } from "react";
import { Download, FlaskConical, Loader2, ScanLine, Wand2 } from "lucide-react";
import { encodeStego, saveBlob } from "../api.js";
import { formatBytes } from "../utils.js";
import { Alert, Badge, CardTitle } from "./ui.jsx";

export default function DemoLab({ onAnalyzeFile }) {
  const [carrier, setCarrier] = useState(null);
  const [mode, setMode] = useState("demo"); // demo | image | text
  const [secretImage, setSecretImage] = useState(null);
  const [secretText, setSecretText] = useState("StegoVision test message: the hidden payload was recovered ✓");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!result) return setPreviewUrl(null);
    const u = URL.createObjectURL(result.blob);
    setPreviewUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [result]);

  const generate = async () => {
    setBusy(true); setError(null); setResult(null);
    try {
      if (mode === "image" && !secretImage) throw new Error("Choose a PNG secret image first.");
      if (mode === "text" && !secretText.trim()) throw new Error("Enter some secret text first.");
      setResult(await encodeStego({
        carrier,
        secretImage: mode === "image" ? secretImage : null,
        secretText: mode === "text" ? secretText : null,
      }));
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  };

  const radio = (value, label) => (
    <label className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${mode === value ? "border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold shadow-xs" : "border-emerald-900/15 bg-white text-slate-700 hover:bg-emerald-50/60"}`}>
      <input type="radio" name="mode" className="accent-emerald-600" checked={mode === value} onChange={() => setMode(value)} /> {label}
    </label>
  );

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h2 className="flex items-center gap-2 text-2xl font-extrabold text-slate-900"><FlaskConical className="h-6 w-6 text-emerald-600" aria-hidden="true" /> Test lab</h2>
      <p className="mt-1 text-sm text-slate-600">
        Create a test stego image using StegoVision's <strong className="font-semibold text-slate-900">own custom LSB format (SVAI v1)</strong>, then analyze it
        to verify the full detect → extract → recover pipeline. This format is <strong className="font-semibold text-slate-900">not</strong> compatible with
        OpenStego, Steghide, OutGuess or other third-party tools.
      </p>

      <div className="card mt-6 space-y-5">
        <div>
          <label className="label" htmlFor="carrier">Carrier image (optional — PNG/JPEG/BMP; a synthetic 512×512 carrier is used if empty)</label>
          <input id="carrier" type="file" accept=".png,.jpg,.jpeg,.bmp" onChange={(e) => setCarrier(e.target.files?.[0] || null)}
                 className="mt-1 block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border file:border-emerald-900/15 file:bg-emerald-50 file:px-3 file:py-1.5 file:text-emerald-900 hover:file:bg-emerald-100 transition" />
        </div>
        <div>
          <div className="label mb-2">Hidden content</div>
          <div className="flex flex-wrap gap-2">{radio("demo", "Demo secret image")}{radio("image", "My PNG image")}{radio("text", "Text message")}</div>
          {mode === "image" && (
            <input aria-label="Secret PNG image" type="file" accept=".png,image/png" onChange={(e) => setSecretImage(e.target.files?.[0] || null)}
                   className="mt-3 block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border file:border-emerald-900/15 file:bg-emerald-50 file:px-3 file:py-1.5 file:text-emerald-900 hover:file:bg-emerald-100 transition" />
          )}
          {mode === "text" && (
            <textarea aria-label="Secret text" value={secretText} onChange={(e) => setSecretText(e.target.value)} rows={3}
                      className="mt-3 w-full rounded-lg border border-emerald-900/20 bg-white p-3 font-mono text-sm text-slate-900 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none shadow-xs" />
          )}
        </div>
        <button className="btn-primary" onClick={generate} disabled={busy}>
          {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Wand2 className="h-4 w-4" aria-hidden="true" />} Generate stego image
        </button>
        {error && <Alert title="Could not generate">{error}</Alert>}
      </div>

      {result && (
        <div className="card mt-4">
          <CardTitle icon={FlaskConical} title="Generated test image" right={<Badge tone="success">SVAI v1 custom format</Badge>} />
          <div className="grid gap-4 sm:grid-cols-[200px_1fr]">
            <img src={previewUrl || undefined} alt="Generated stego test image" className="w-full rounded-lg border border-emerald-900/10 shadow-2xs" />
            <div className="space-y-1.5 text-sm text-slate-700">
              <p>Hidden payload: <span className="font-mono font-semibold text-slate-900">{result.info.payloadType}</span> · {formatBytes(result.info.payloadBytes)} of {formatBytes(result.info.capacityBytes)} capacity</p>
              <p>Carrier: {result.info.demoCarrier ? "generated demo carrier" : "your upload"} · Payload: {result.info.demoPayload ? "generated demo image" : "your content"}</p>
              <p className="text-xs text-slate-500">The image looks unchanged to the eye (each colour value changes by at most 1). Output is always a lossless PNG — re-saving as JPEG would destroy the payload.</p>
              <div className="flex flex-wrap gap-2 pt-2">
                <button className="btn-ghost" onClick={() => saveBlob(result.blob, "stego_test_image.png")}><Download className="h-4 w-4" aria-hidden="true" /> Download</button>
                <button className="btn-primary" onClick={() => onAnalyzeFile(new File([result.blob], "stego_test_image.png", { type: "image/png" }))}><ScanLine className="h-4 w-4" aria-hidden="true" /> Analyze this image</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
