"""Framework-agnostic application service. The FastAPI layer is a thin wrapper around this."""
import hashlib
import os
import re
import time
from datetime import datetime, timezone

from PIL import Image

from . import __version__
from .config import get_settings
from .core import demo, detection, extraction, lsb, metadata, report, statistics
from .core.payload import PayloadError, validate_payload
from .core.stego_format import TYPE_PNG, TYPE_TEXT, capacity_bytes, encode_to_png_bytes
from .core.validation import rgb_array, validate_image
from .errors import AppError, NotFoundError, ValidationError
from .storage import Store

_store = None


def get_store() -> Store:
    global _store
    if _store is None:
        _store = Store(get_settings().ttl_seconds)
    return _store


def reset_store():
    """Test helper."""
    global _store
    if _store is not None:
        _store.purge_all()
    _store = None


def sanitize_filename(name) -> str:
    name = os.path.basename((name or "upload").replace("\\", "/"))
    name = re.sub(r"[^\w.\- ()]", "_", name)[:120].strip(" .")
    return name or "upload"


def analyze(filename, data: bytes) -> dict:
    t0 = time.perf_counter()
    settings = get_settings()
    v = validate_image(data, settings)
    rgb = rgb_array(v.image)
    meta = metadata.analyze_metadata(data, v.image, v.format)
    stats = statistics.analyze_statistics(rgb)
    lsb_res = lsb.analyze_lsb(rgb)
    ctx = detection.Context(data, v.format, rgb, meta, stats, lsb_res, settings)
    det = detection.run_pipeline(ctx)
    analysis_id = get_store().new_id()
    record = {
        "analysis_id": analysis_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "filename": sanitize_filename(filename),
        "sha256": hashlib.sha256(data).hexdigest(),
        "file_size_bytes": len(data),
        "image": {"format": v.format, "width": v.width, "height": v.height, "mode": v.mode,
                  "megapixels": round(v.width * v.height / 1e6, 3),
                  "lsb_capacity_bytes": capacity_bytes(v.width, v.height)},
        "metadata": meta,
        "statistics": stats,
        "lsb": lsb_res,
        "detection": det,
        "extraction": {"status": "not_attempted", "methods_attempted": [], "recovered": None, "possible_reasons": []},
        "limitations": det["limitations"],
        "duration_ms": 0,
        "tool_version": __version__,
    }
    record["duration_ms"] = int((time.perf_counter() - t0) * 1000)
    files = {"original": data, "lsb": lsb.lsb_visualization_png(rgb)}
    get_store().put(analysis_id, record, files)
    return report.public_view(record)


def get_analysis(analysis_id: str) -> dict:
    return report.public_view(get_store().get(analysis_id))


def extract(analysis_id: str) -> dict:
    store = get_store()
    store.get(analysis_id)
    data = store.read_file(analysis_id, "original")
    if data is None:
        raise NotFoundError("The original upload is no longer available.")
    settings = get_settings()
    v = validate_image(data, settings)
    result, payload = extraction.run_extraction(data, v.format, v.image, settings)
    result["attempted_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if payload is not None:
        store.write_file(analysis_id, "recovered", payload)
    else:
        store.delete_file(analysis_id, "recovered")
    store.update(analysis_id, extraction=result)
    return report.public_view(store.get(analysis_id))


def get_recovered(analysis_id: str):
    store = get_store()
    rec = store.get(analysis_id)
    info = rec["extraction"].get("recovered")
    blob = store.read_file(analysis_id, "recovered")
    if not info or blob is None:
        raise AppError("no_recovered_payload", "No validated recovered payload exists for this analysis. Run extraction first.", 404)
    # Re-validate right before serving (defence in depth).
    validate_payload(TYPE_PNG if info["kind"] == "image" else TYPE_TEXT, blob, get_settings())
    return blob, info["mime_type"], info["filename"]


def get_original(analysis_id: str):
    store = get_store()
    rec = store.get(analysis_id)
    blob = store.read_file(analysis_id, "original")
    if blob is None:
        raise NotFoundError()
    fmt = rec["image"]["format"]
    return blob, {"PNG": "image/png", "JPEG": "image/jpeg", "BMP": "image/bmp"}[fmt]


def get_lsb_visualization(analysis_id: str) -> bytes:
    blob = get_store().read_file(analysis_id, "lsb")
    if blob is None:
        raise NotFoundError()
    return blob


def get_json_report(analysis_id: str) -> bytes:
    return report.build_json(get_store().get(analysis_id))


def get_pdf_report(analysis_id: str) -> bytes:
    store = get_store()
    rec = store.get(analysis_id)
    recovered = store.read_file(analysis_id, "recovered") if rec["extraction"].get("recovered") else None
    info = rec["extraction"].get("recovered")
    return report.build_pdf(rec, original=store.read_file(analysis_id, "original"),
                            recovered=recovered if info and info["kind"] == "image" else None,
                            lsb_png=store.read_file(analysis_id, "lsb"))


def encode_test_image(carrier_bytes, secret_png, secret_text):
    """Create a test stego PNG. Returns (png_bytes, headers_info). Carrier/secret optional (demo mode)."""
    settings = get_settings()
    demo_carrier = carrier_bytes is None
    if demo_carrier:
        carrier = demo.make_demo_carrier()
    else:
        carrier = validate_image(carrier_bytes, settings).image
    if secret_png is not None and secret_text:
        raise ValidationError("ambiguous_payload", "Provide either a secret image or secret text, not both.", 400)
    if secret_png is not None:
        if len(secret_png) > settings.max_payload_bytes:
            raise ValidationError("payload_too_large", "Secret image exceeds the payload size limit.", 413)
        try:
            validate_payload(TYPE_PNG, secret_png, settings)
        except PayloadError as exc:
            raise ValidationError("invalid_secret_image", "Secret image must be a valid PNG file: " + exc.message, 415)
        payload, ptype = secret_png, TYPE_PNG
    elif secret_text:
        payload, ptype = secret_text.encode("utf-8"), TYPE_TEXT
        if len(payload) > settings.max_payload_bytes:
            raise ValidationError("payload_too_large", "Secret text exceeds the payload size limit.", 413)
    else:
        payload, ptype = demo.make_demo_secret(), TYPE_PNG
    out = encode_to_png_bytes(carrier, payload, ptype)
    info = {"payload_type": "png" if ptype == TYPE_PNG else "text", "payload_bytes": len(payload),
            "capacity_bytes": capacity_bytes(*carrier.size), "demo_carrier": demo_carrier,
            "demo_payload": secret_png is None and not secret_text}
    return out, info
