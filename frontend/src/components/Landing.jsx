import React from "react";
import { ArrowRight, Binary, Cpu, FileText, FlaskConical, Layers, Lock, ScanLine, ShieldCheck, Sparkles } from "lucide-react";
import ComicExplainer from "./ComicExplainer.jsx";

const FEATURES = [
  [Layers, "Multi-method forensics", "Metadata and container inspection, pixel statistics, entropy, chi-square and RS analysis on the LSB planes."],
  [Binary, "Separate extraction", "Detection and extraction are independent steps. Recovered payloads are validated before they are shown or downloaded."],
  [Cpu, "Honest AI integration", "A PyTorch hook is ready for a trained model. Without one, AI output is reported as Not Available — never invented."],
  [FileText, "Forensic reports", "Download a PDF or JSON report separating measured findings from heuristics and model output."],
  [Lock, "Safe by design", "Uploads are content-validated, stored under random names in a temp directory, auto-expired, and never executed."],
  [FlaskConical, "End-to-end test lab", "Create a test stego image in the custom StegoVision format and watch it be detected and recovered."],
];

export default function Landing({ onStart, onLab, onComics }) {
  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="grid-bg absolute inset-0" aria-hidden="true" />
        <div className="relative mx-auto max-w-5xl px-6 pb-16 pt-16 text-center">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-600/25 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800 shadow-xs">
            <ScanLine className="h-3.5 w-3.5 text-emerald-700" aria-hidden="true" /> Image steganography analysis workbench
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">
            Find what an image <span className="bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">is hiding</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-slate-600 sm:text-lg">
            Upload a suspicious image. StegoVision AI runs forensic detection, attempts compatible extraction, and
            produces an evidence-grade report — with its limitations stated plainly.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button className="btn-primary" onClick={onStart}>Analyze an image <ArrowRight className="h-4 w-4" aria-hidden="true" /></button>
            <button className="btn-ghost" onClick={onLab}><FlaskConical className="h-4 w-4 text-emerald-700" aria-hidden="true" /> Open test lab</button>
            <button className="btn-ghost" onClick={() => document.getElementById("comics-section")?.scrollIntoView({ behavior: "smooth" })}>
              <Sparkles className="h-4 w-4 text-emerald-700" aria-hidden="true" /> Real-time comics
            </button>
          </div>
        </div>
      </section>

      {/* Interactive Comics Section */}
      <div id="comics-section" className="border-y border-emerald-900/10 bg-emerald-50/20 py-6">
        <ComicExplainer onAnalyzeDemo={onLab} />
      </div>

      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl font-extrabold text-slate-900">Comprehensive Forensic Architecture</h2>
          <p className="text-sm text-slate-600 mt-1">Multi-layered detection and content extraction built for evidence-grade analysis</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(([Icon, title, text]) => (
            <div key={title} className="card hover:border-emerald-500/30 hover:shadow-md transition">
              <Icon className="mb-3 h-5 w-5 text-emerald-600" aria-hidden="true" />
              <h3 className="font-bold text-slate-900">{title}</h3>
              <p className="mt-1.5 text-sm text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 pb-24">
        <div className="card border-amber-300/80 bg-amber-50/40">
          <h2 className="mb-2 flex items-center gap-2 font-bold text-amber-900"><ShieldCheck className="h-4 w-4 text-amber-700" aria-hidden="true" /> What this tool can and cannot do</h2>
          <ul className="list-disc space-y-1.5 pl-5 text-sm text-slate-700">
            <li>Detection is statistical and can produce false positives and false negatives.</li>
            <li>Automatic extraction supports StegoVision custom LSB format (SVAI v1), raw LSB embedded images, appended PNG/JPEG/BMP files, and plain text.</li>
            <li>Lossy re-compression (JPEG) destroys spatial LSB payloads, and DCT-domain steganography is not analysed.</li>
            <li>High entropy or odd metadata alone is never treated as proof.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
