"""Forensic report generation: structured JSON and PDF (ReportLab)."""
import io
import json
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

TOOL = "StegoVision AI"


def to_builtin(obj):
    """Make numpy scalars/arrays JSON serialisable."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if isinstance(obj, dict):
        return {str(k): to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_builtin(v) for v in obj]
    if np is not None:
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    return obj


def public_view(record: dict) -> dict:
    """Strip internal-only fields; used for API responses and the JSON report."""
    return to_builtin({k: v for k, v in record.items() if not k.startswith("_")})


def build_json(record: dict) -> bytes:
    doc = public_view(record)
    doc.setdefault("report_notes", {
        "measured": "Values computed directly from the file's bytes/pixels.",
        "heuristic": "Interpretations derived from statistical tests with known false-positive/negative rates.",
        "model": "Output of a trained classifier; only present when a model is actually loaded.",
    })
    return json.dumps(doc, indent=2, ensure_ascii=False).encode("utf-8")


def _thumb(png_or_any: bytes, box=60 * mm):
    img = Image.open(io.BytesIO(png_or_any))
    img.load()
    img = img.convert("RGB")
    img.thumbnail((512, 512))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    w, h = img.size
    scale = min(box / w, box / h)
    return RLImage(buf, width=w * scale, height=h * scale)


def build_pdf(record: dict, original: bytes = None, recovered: bytes = None, lsb_png: bytes = None) -> bytes:
    rec = public_view(record)
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9, leading=12)
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.HexColor("#444444"))
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, textColor=colors.HexColor("#0b3b3c"))
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, textColor=colors.HexColor("#0b3b3c"), spaceBefore=10)
    cell = ParagraphStyle("cell", parent=body, fontSize=8.5, leading=11)

    def P(text, style=body):
        return Paragraph(escape(str(text)), style)

    def kv(rows, widths=(45 * mm, 120 * mm)):
        t = Table([[P(k, cell), P(v, cell)] for k, v in rows], colWidths=widths)
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b8c4c4")),
                               ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4f4")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return t

    img = rec.get("image", {})
    det = rec.get("detection", {})
    ext = rec.get("extraction", {})
    meta = rec.get("metadata", {}).get("measured", {})
    stats = rec.get("statistics", {}).get("measured", {})
    lsb = rec.get("lsb", {})
    story = [P("StegoVision AI — Forensic Analysis Report", h1),
             P("Automated analysis. Findings are labelled [MEASURED], [HEURISTIC] or [MODEL]. "
               "This report is investigative guidance, not conclusive proof.", small), Spacer(1, 6)]

    story += [P("1. Case information", h2), kv([
        ("Analysis ID", rec.get("analysis_id")), ("Timestamp (UTC)", rec.get("timestamp")),
        ("Original filename", rec.get("filename")), ("SHA-256", rec.get("sha256")),
        ("File size", f"{rec.get('file_size_bytes')} bytes"),
        ("Format / mode", f"{img.get('format')} / {img.get('mode')}"),
        ("Dimensions", f"{img.get('width')} x {img.get('height')} px")])]

    story += [P("2. Detection outcome", h2), kv([
        ("Outcome", det.get("outcome")), ("Explanation", det.get("explanation"))])]
    rows = [(d["name"], f"[{d['kind'].upper()}] {d['signal']}: {d['summary']}") for d in det.get("detectors", [])]
    if rows:
        story += [Spacer(1, 4), kv(rows)]

    ai = det.get("ai") or {}
    story += [P("3. AI model prediction [MODEL]", h2)]
    if ai.get("available"):
        story.append(kv([("Prediction", ai.get("prediction")), ("Confidence", ai.get("confidence")),
                         ("Note", ai.get("note"))]))
    else:
        story.append(kv([("Status", "Not available"), ("Reason", ai.get("reason")), ("Confidence", "Not Available")]))

    story += [P("4. Metadata findings [MEASURED]", h2), kv([
        ("EXIF fields", meta.get("exif_field_count")), ("Text fields", len(meta.get("text_fields", {}))),
        ("Trailing data", f"{meta.get('trailing_data_bytes', 0)} bytes"
         + (f" ({meta.get('trailing_data_type')})" if meta.get("trailing_data_type") else ""))])]
    for o in rec.get("metadata", {}).get("observations", []):
        story.append(P(f"• [{o['severity']}] {o['message']}", body))

    story += [P("5. Statistical findings [MEASURED]", h2), kv([
        ("Grayscale entropy", f"{stats.get('grayscale_entropy_bits')} bits"),
        ("Laplacian variance", stats.get("laplacian_variance")),
        ("Unique gray levels", stats.get("unique_gray_levels")),
        ("Saturated pixel fraction", stats.get("saturated_pixel_fraction"))])]
    for line in rec.get("statistics", {}).get("interpretation", []):
        story.append(P(f"• [HEURISTIC] {line}", body))

    story += [P("6. LSB analysis", h2)]
    bs = lsb.get("bit_statistics", {})
    story.append(kv([(f"LSB {c} [MEASURED]", f"ones ratio {v['ones_ratio']}, bit entropy {v['bit_entropy']}, "
                                              f"horizontal agreement {v['horizontal_agreement']}") for c, v in bs.items()]))
    rs = lsb.get("rs_analysis", {})
    story.append(kv([("RS estimated modified fraction [HEURISTIC]", rs.get("mean_estimated_payload_fraction")),
                     ("Chi-square windows [MEASURED]",
                      "; ".join(f"{w['samples']} samples: p={w.get('p_value', 'n/a')}" for w in lsb.get('chi_square_windows', [])))]))
    if lsb_png:
        story += [Spacer(1, 4), P("LSB bit-plane visualisation (forensic view — NOT a recovered image):", small), _thumb(lsb_png)]

    story += [P("7. Extraction", h2), kv([("Status", ext.get("status")), ("Attempted at", ext.get("attempted_at"))])]
    for a in ext.get("methods_attempted", []):
        story.append(P(f"• {a['method']}: {a['status']} — {a.get('message')}", body))
    rv = ext.get("recovered")
    if rv:
        rows = [("Kind", rv.get("kind")), ("Filename", rv.get("filename")), ("Format", rv.get("format")),
                ("Size", f"{rv.get('size_bytes')} bytes"), ("SHA-256", rv.get("sha256")), ("Method", rv.get("method"))]
        if rv.get("kind") == "image":
            rows.append(("Dimensions", f"{rv.get('width')} x {rv.get('height')} px"))
        story.append(kv(rows))
        if rv.get("kind") == "image" and recovered:
            story += [Spacer(1, 4), P("Recovered image thumbnail:", small), _thumb(recovered)]
        if rv.get("kind") == "text":
            story.append(P("Recovered text (first 1000 chars): " + rv.get("text_preview", "")[:1000], body))
    elif ext.get("status") == "failed":
        story.append(P("Possible reasons: " + " ".join(ext.get("possible_reasons", [])), body))
    elif ext.get("status") == "not_attempted":
        story.append(P("Extraction was not attempted for this analysis.", body))

    story += [P("8. Technical limitations", h2)] + [P(f"• {x}", body) for x in rec.get("limitations", [])]
    story.append(Spacer(1, 6))
    story.append(P(f"Generated by {TOOL}. Custom-format extraction applies only to StegoVision SVAI v1 payloads.", small))

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                      bottomMargin=16 * mm, title="StegoVision AI Forensic Report", author=TOOL).build(story)
    return buf.getvalue()
