"""Pluggable detection pipeline.

Each detector is a function `fn(ctx) -> dict` registered with `@register_detector(name)`.
It returns:
    {"name", "kind": "measured"|"heuristic"|"model", "signal": one of SIGNALS,
     "summary": str, "details": dict}
`combine()` then turns the signals into one of the three allowed outcomes. To add a new
method (or a trained model), register another detector -- no other code changes needed.
"""
from dataclasses import dataclass, field

import numpy as np

from ..config import Settings
from . import ml
from .validation import LOSSLESS

OUTCOME_NONE = "No Strong Evidence Detected"
OUTCOME_POSSIBLE = "Possible Steganography Detected"
OUTCOME_INCONCLUSIVE = "Inconclusive"

# signal vocabulary
STRONG_FOR, FOR, NEUTRAL, AGAINST, NA = "strong_for", "for", "neutral", "against", "not_applicable"

RS_FOR, RS_AGAINST = 0.12, 0.05  # thresholds calibrated ONLY on synthetic images (see README)
CHI_HIGH = 0.95


@dataclass
class Context:
    data: bytes
    fmt: str
    rgb: np.ndarray
    metadata: dict
    statistics: dict
    lsb: dict
    settings: Settings
    extras: dict = field(default_factory=dict)


DETECTORS = []


def register_detector(name):
    def deco(fn):
        DETECTORS.append((name, fn))
        return fn
    return deco


def _lsb_applicable(ctx: Context):
    h, w, _ = ctx.rgb.shape
    if ctx.fmt not in LOSSLESS:
        return False, "Lossy format (JPEG): spatial LSB tests are not meaningful after lossy compression, and DCT-domain steganography is not analysed."
    if h * w < 64 * 64:
        return False, "Image is too small (<64x64) for reliable statistical tests."
    return True, None


@register_detector("custom_signature")
def det_signature(ctx):
    probe = ctx.lsb["custom_header_probe"]
    if probe.get("signature_found"):
        return {"name": "custom_signature", "kind": "measured", "signal": STRONG_FOR,
                "summary": "A StegoVision (SVAI) header signature was found in the pixel LSBs. "
                           "This is a measured match against this project's own format only.",
                "details": {k: probe[k] for k in ("version", "type_id", "length") if k in probe}}
    return {"name": "custom_signature", "kind": "measured", "signal": NEUTRAL,
            "summary": "No StegoVision (SVAI) signature in the pixel LSBs. This says nothing about other embedding methods.",
            "details": {}}


@register_detector("trailing_data")
def det_trailing(ctx):
    m = ctx.metadata["measured"]
    n, kind = m.get("trailing_data_bytes", 0), m.get("trailing_data_type")
    if not n:
        return {"name": "trailing_data", "kind": "measured", "signal": NEUTRAL,
                "summary": "No data appended after the end of the image.", "details": {}}
    if kind:
        return {"name": "trailing_data", "kind": "measured", "signal": STRONG_FOR,
                "summary": f"{n} bytes after the image end begin with a {kind} signature: appended file content.",
                "details": {"bytes": n, "type": kind}}
    return {"name": "trailing_data", "kind": "heuristic", "signal": FOR,
            "summary": f"{n} unidentified bytes follow the image end. Unusual, but some tools append harmless data.",
            "details": {"bytes": n}}


@register_detector("rs_analysis")
def det_rs(ctx):
    ok, why = _lsb_applicable(ctx)
    if not ok:
        return {"name": "rs_analysis", "kind": "heuristic", "signal": NA, "summary": why, "details": {}}
    rs = ctx.lsb["rs_analysis"]
    if not rs["valid"]:
        return {"name": "rs_analysis", "kind": "heuristic", "signal": NA,
                "summary": "RS analysis could not produce a valid estimate for this image.", "details": {}}
    est = rs["mean_estimated_payload_fraction"]
    if est >= RS_FOR:
        sig, msg = FOR, f"RS analysis estimates ~{est:.0%} of LSB capacity may be modified (threshold {RS_FOR:.0%})."
    elif est < RS_AGAINST:
        sig, msg = AGAINST, f"RS analysis estimates a negligible modified-LSB fraction (~{est:.1%})."
    else:
        sig, msg = NEUTRAL, f"RS estimate (~{est:.1%}) is in the ambiguous range between {RS_AGAINST:.0%} and {RS_FOR:.0%}."
    return {"name": "rs_analysis", "kind": "heuristic", "signal": sig, "summary": msg,
            "details": {"estimated_payload_fraction": est}}


@register_detector("chi_square")
def det_chi(ctx):
    ok, why = _lsb_applicable(ctx)
    if not ok:
        return {"name": "chi_square", "kind": "heuristic", "signal": NA, "summary": why, "details": {}}
    valid = [w for w in ctx.lsb["chi_square_windows"] if w.get("valid")]
    if not valid:
        return {"name": "chi_square", "kind": "heuristic", "signal": NA,
                "summary": "Chi-square test not applicable (too few populated value pairs).", "details": {}}
    hi = [w for w in valid if w["p_value"] > CHI_HIGH]
    if hi:
        return {"name": "chi_square", "kind": "heuristic", "signal": FOR,
                "summary": "Pairs-of-values are equalised in at least one prefix window. This matches dense LSB replacement but also occurs in noisy natural images, so it is only corroborating.",
                "details": {"windows_over_threshold": [w["samples"] for w in hi]}}
    return {"name": "chi_square", "kind": "heuristic", "signal": AGAINST,
            "summary": "Pairs-of-values are clearly unequal in every tested window, arguing against dense sequential LSB replacement.",
            "details": {}}


@register_detector("ai_model")
def det_model(ctx):
    res = ml.run_model(ctx.rgb, ctx.settings.model_path)
    ctx.extras["ai"] = res
    if not res["available"]:
        return {"name": "ai_model", "kind": "model", "signal": NA,
                "summary": "AI classification unavailable: " + (res.get("reason") or "no model"), "details": {}}
    sig = FOR if res["prediction"] == "stego" and res["confidence"] >= 0.9 else NEUTRAL
    return {"name": "ai_model", "kind": "model", "signal": sig,
            "summary": f"Model predicts '{res['prediction']}' (confidence {res['confidence']:.2f}).", "details": res}


def combine(results: list) -> tuple:
    s = {r["name"]: r["signal"] for r in results}
    if any(v == STRONG_FOR for v in s.values()):
        return OUTCOME_POSSIBLE, "Strong, directly measured indicator(s) of embedded or appended content were found."
    corroborators = [k for k in ("chi_square", "ai_model", "trailing_data") if s.get(k) == FOR]
    if s.get("rs_analysis") == FOR and corroborators:
        return OUTCOME_POSSIBLE, "RS analysis and at least one independent indicator both point towards LSB embedding."
    if s.get("ai_model") == FOR and s.get("trailing_data") == FOR:
        return OUTCOME_POSSIBLE, "Model prediction and appended-data finding agree."
    if s.get("rs_analysis") == AGAINST and not any(s.get(k) == FOR for k in ("trailing_data", "ai_model")):
        return OUTCOME_NONE, "Statistical LSB tests found no strong evidence. This does not rule out other or lightly-used embedding methods."
    if any(v == FOR for v in s.values()):
        return OUTCOME_INCONCLUSIVE, "Some weak indicators were found but they are not corroborated by independent evidence."
    return OUTCOME_INCONCLUSIVE, "The available tests are not applicable or not informative for this image."


LIMITATIONS = [
    "Detection is statistical. False positives (clean images flagged) and false negatives (hidden data missed) both occur.",
    "RS and chi-square tests target sequential/LSB-replacement style embedding in lossless pixel data; they are weak against small payloads, adaptive/matching embedding, key-based pixel scattering, encryption-aware schemes and DCT-domain (JPEG) methods.",
    "Thresholds were calibrated on synthetic test images only, not on a large corpus of real photographs.",
    "High entropy, metadata anomalies and appended data do not by themselves prove steganography.",
    "Extraction only supports the StegoVision custom LSB format (SVAI v1) and appended PNG files; other formats and tools cannot be decoded automatically.",
]


def run_pipeline(ctx: Context) -> dict:
    results = [fn(ctx) for _, fn in DETECTORS]
    outcome, reason = combine(results)
    ai = ctx.extras.get("ai") or {"available": False, "prediction": None, "confidence": None,
                                  "reason": "Model not run."}
    return {"outcome": outcome, "explanation": reason, "detectors": results, "ai": ai,
            "limitations": list(LIMITATIONS)}
