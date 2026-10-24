# StegoVision AI

**AI-ready image steganography detection and hidden-content extraction.**
React + Vite + Tailwind frontend, FastAPI backend, no paid APIs or keys required.

> **Read this first.** Detection is statistical and produces both false positives and false negatives.
> Automatic extraction works **only** for (a) StegoVision's own custom LSB format (*SVAI v1*, defined below) and
> (b) a PNG file appended after an image's end marker. It cannot decode OpenStego, Steghide, OutGuess, F5, keyed
> or scattered-pixel schemes, and nothing survives lossy re-compression. No AI model ships with this repo, so AI output
> is reported as **Not Available** unless you supply a trained checkpoint.

## Features

- Upload validation from **file contents** (PNG/JPEG/BMP magic bytes + full decode), size/dimension/pixel limits, corrupted-file handling.
- Forensics: metadata & container inspection (EXIF, PNG chunks, **trailing data**), pixel statistics & entropy, LSB bit-plane statistics, chi-square (pairs of values) over growing prefixes, RS analysis payload estimate.
- Pluggable detection pipeline → exactly one of `No Strong Evidence Detected`, `Possible Steganography Detected`, `Inconclusive`.
- Separate **extraction** step with its own status; every recovered payload is re-validated from its bytes (real PNG decode / strict UTF-8) before preview or download.
- Custom LSB **encoder + decoder** (library, CLI, REST endpoint, UI test lab).
- PDF (ReportLab) and JSON reports; findings tagged **[MEASURED] / [HEURISTIC] / [MODEL]**.
- Dashboard: original vs recovered, detection status, metadata/statistics/LSB/AI/extraction cards, LSB visualization panel clearly labelled *not a recovered image*.

## Repository layout

```
backend/
  app/
    main.py            FastAPI factory, CORS, error handlers
    api.py             thin HTTP routes
    service.py         all application logic (framework-agnostic, fully unit-tested)
    storage.py         ephemeral temp-dir store with TTL, random IDs, whitelisted artefact kinds
    config.py, errors.py
    core/
      validation.py    content-based image validation
      metadata.py      EXIF / PNG chunks / trailing-data inspection
      statistics.py    entropy, histograms, correlation, noise
      lsb.py           bit-plane stats, chi-square, RS analysis, visualization
      detection.py     detector registry + decision rules
      ml.py            optional PyTorch classifier hook (no weights included)
      stego_format.py  SVAI v1 encoder/decoder
      payload.py       recovered-payload validation
      extraction.py    extraction methods registry
      report.py        JSON + PDF reports
      demo.py          deterministic synthetic carrier/secret images
  tools/               stego_cli.py, make_test_images.py
  tests/               pytest suite (45 tests + HTTP tests)
frontend/              React app (src/api.js talks to the real backend)
render.yaml            Render blueprint        backend/Procfile, railway.json  Railway
frontend/vercel.json   Vercel
```

## Run locally

Requires Python 3.10+ and Node 18+.

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # optional; defaults work for local dev
uvicorn app.main:app --reload   # http://127.0.0.1:8000  (docs at /docs)

# frontend (second terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173 — /api is proxied to :8000
```

Open the app → **Test lab** → *Generate stego image* → *Analyze this image* → *Run analysis* → *Attempt Extraction*.
The hidden image appears next to the original and its bytes match what was embedded.

### Generate test images and verify extraction (CLI)

```bash
cd backend
python -m tools.make_test_images               # writes ./samples/*.png (git-ignored)
python -m tools.stego_cli decode --image samples/stego_image.png --out recovered
cmp recovered.png samples/secret.png && echo "identical"

python -m tools.stego_cli encode --carrier my_cover.png --secret-text "meet at dawn" --out my_stego.png
python -m tools.stego_cli encode --carrier my_cover.png --secret-image my_secret.png --out my_stego.png
python -m tools.stego_cli decode --image samples/clean.png --out nothing      # fails with an explanation
```

Samples: `carrier`, `secret`, `stego_image` (hidden PNG), `stego_text`, `clean`, `appended_png` (PNG appended after IEND),
`corrupted_stego` (one payload bit flipped → CRC failure).

## Custom format: StegoVision SVAI v1

**Project-specific. Not compatible with any third-party steganography tool.**

- Carrier samples = R, G, B values of each pixel, row-major, channel-interleaved (alpha untouched). 1 payload bit per sample in the LSB, MSB-first. Output is always lossless PNG; the carrier input is never modified.
- Bit stream = 15-byte big-endian header + payload.

| field | size | meaning |
|---|---|---|
| magic | 4 | `SVAI` |
| version | 1 | `1` |
| type | 1 | `1` UTF-8 text, `2` PNG image |
| flags | 1 | reserved `0` |
| length | 4 | payload bytes |
| crc32 | 4 | CRC-32 of payload |

Capacity = `floor(W·H·3 / 8) − 15` bytes. The decoder checks signature → version → type → length ≤ capacity → CRC-32, then
validates the payload (PNG must fully decode; text must be strict UTF-8) before it is ever shown.

## API

| Method & path | Purpose |
|---|---|
| `GET /api/health` | status, limits, whether an AI model is loaded |
| `POST /api/analyze` (multipart `file`) → 201 | forensic analysis; returns the full result incl. `analysis_id` |
| `GET /api/analysis/{id}` | stored result |
| `POST /api/extract/{id}` | run extraction (200 even when extraction *fails*; check `extraction.status`) |
| `GET /api/analysis/{id}/report` | PDF report |
| `GET /api/analysis/{id}/json` | JSON report |
| `GET /api/analysis/{id}/recovered` | validated recovered file (404 until extraction succeeds) |
| `GET /api/analysis/{id}/original` · `/lsb-visualization` | image previews used by the UI |
| `POST /api/stego/encode` (multipart: optional `carrier`, `secret_image` (PNG) or `secret_text`) | create a test stego PNG; no inputs → demo mode |

Errors are `{"error": {"code": "...", "message": "..."}}` with 400/404/413/415/422 as appropriate.

## Detection method & limitations

| Detector | Kind | Notes |
|---|---|---|
| `custom_signature` | measured | SVAI header in LSBs (strong, but only for this project's format) |
| `trailing_data` | measured/heuristic | bytes after the image end; known file signature = strong, unknown bytes = weak |
| `rs_analysis` | heuristic | Fridrich RS estimate of modified LSB fraction; `≥12%` for, `<5%` against |
| `chi_square` | heuristic | pairs-of-values on 16K/64K/256K/full prefixes; high p only *corroborates* (noisy clean images also score high) |
| `ai_model` | model | only if a trained checkpoint is configured |

Decision: any strong indicator → *Possible*; RS “for” **plus** an independent indicator → *Possible*; RS “against” and no
weak indicators → *No Strong Evidence*; everything else (JPEG, tiny images, lone weak signals) → *Inconclusive*.
High entropy and metadata oddities are reported but never decisive.

Known limitations:
- RS/chi-square target LSB **replacement** in lossless pixels. Small payloads, LSB *matching*, adaptive/keyed/scattered embedding, encrypted payloads and DCT-domain (JPEG) methods are largely invisible to them.
- Thresholds were calibrated **only on synthetic images** (clean: RS ≈ 0–7 %; 10 % / 50 % / 100 % random embedding: ≈ 10–18 % / 48–52 % / 91–97 %). Real photographs, screenshots, graphics and heavily processed images can produce false positives *and* negatives. Treat results as leads, not evidence.
- “No Strong Evidence” does **not** mean “clean”.

### Adding a trained model
`backend/app/core/ml.py` defines `StegoCNN` and loads a checkpoint from `STEGO_MODEL_PATH` (`pip install -r requirements-ml.txt`).
No weights are bundled, and you must train/validate your own (ideally on cover/stego pairs matching your threat model).
Until a model loads, the API/UI/report show `Not Available` and no confidence value is produced. To add other detectors
use `@register_detector` in `detection.py`; to add extractors append to `EXTRACTORS` in `extraction.py`.

## Security notes

- Uploaded and recovered bytes are only parsed as data (Pillow decode, UTF-8 decode) — never executed or imported.
- Format determined from magic bytes + full decode; decompression-bomb guard via `MAX_PIXELS`; 413/415/422 for violations; uploads read with a hard byte cap.
- Files live in a private `0700` temp directory under `<random-uuid>/<whitelisted-kind>.bin`; IDs must match `^[0-9a-f]{32}$`; no client string touches a path (path traversal tested). Results expire after `RESULT_TTL_SECONDS` and are purged at exit. Nothing is kept permanently.
- Recovered payloads are re-validated immediately before serving; downloads send `X-Content-Type-Options: nosniff` and `Content-Disposition: attachment`.
- CORS only for `ALLOWED_ORIGINS` (no wildcard). No secrets in the frontend; the only frontend env var is the public API base URL.
- Not included: authentication and rate limiting. Put the API behind your platform's rate limiting/WAF before exposing it publicly.

## Deployment

State is in-memory plus an ephemeral temp dir, so **run a single worker** (`--workers 1`, already set) and expect results to disappear on restart/redeploy — acceptable because results are short-lived by design.

**Backend → Render:** New *Blueprint* from this repo (`render.yaml`) or a Web Service with root `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`. Set `ALLOWED_ORIGINS=https://<your-frontend>.vercel.app`.

**Backend → Railway:** New project from repo, root directory `backend` (uses `railway.json`/`Procfile`). Set `ALLOWED_ORIGINS`.

**Frontend → Vercel:** Import repo, root directory `frontend` (Vite preset; `vercel.json` included). Set `VITE_API_BASE_URL=https://<your-backend-host>` (no trailing slash), then redeploy. Add the Vercel URL to the backend's `ALLOWED_ORIGINS` (comma-separated for several).

## Tests

```bash
cd backend && pytest -q
```
Covers valid uploads (PNG/JPEG/BMP), invalid/unsupported/empty/oversized/corrupted/truncated files, clean images, known-format stego, hidden text, hidden image, corrupted payloads (CRC, bad length, bad version/type, valid-CRC-but-not-a-PNG), appended PNG, JPEG handling, report generation (incl. hostile text), path-traversal IDs, expiry, concurrency, detector extensibility, and the **end-to-end** test (embed secret PNG → upload → analyze → extract → recovered bytes identical). `tests/test_api.py` repeats the flow over HTTP with FastAPI's TestClient plus CORS and error-shape checks.

## Verification status

The development sandbox had no network access, so not everything could be executed there:

| Component | Status |
|---|---|
| Backend core, service layer, CLI, reports, 45 pytest-style tests | **Executed and passing** (run through a minimal pytest-compatible runner because pytest was not installable) |
| Mutation checks (CRC check removed, RS rule disabled) | Tests fail as expected |
| PDF output | Rendered and visually inspected |
| React components | Bundled with esbuild and **server-rendered** for every view/state with real backend output; no errors |
| FastAPI routes (`api.py`, `main.py`) and `tests/test_api.py` | **Written but not executed** (FastAPI not installable offline) — run `pytest` locally first |
| Vite/Tailwind build, browser behaviour (drag-drop, XHR progress, PDF iframe), PyTorch hook | **Not executed** — run `npm run build` / `npm run dev` locally |
| Deployment configs | Written from platform docs conventions, not deployed |

If `pytest` or `npm run build` reports anything, those are the places to look first.
