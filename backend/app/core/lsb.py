"""LSB-plane analysis: bit statistics, chi-square (pairs of values), RS analysis, visualisation.

Measured numbers come from the pixels. Interpretation is left to the detection module.
Neither test is a proof: both have known false-positive / false-negative cases.
"""
import io

import numpy as np
from PIL import Image
from scipy.stats import chi2

from .stego_format import parse_header

CHANNELS = ("red", "green", "blue")


def lsb_statistics(rgb: np.ndarray) -> dict:
    out = {}
    for i, n in enumerate(CHANNELS):
        plane = (rgb[:, :, i] & 1).astype(np.uint8)
        ones = float(plane.mean())
        p = min(max(ones, 1e-12), 1 - 1e-12)
        ent = float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))
        horiz = float((plane[:, 1:] == plane[:, :-1]).mean())  # 0.5 for random bits
        out[n] = {"ones_ratio": round(ones, 5), "bit_entropy": round(ent, 5), "horizontal_agreement": round(horiz, 5)}
    return out


def chi_square_pov(samples: np.ndarray) -> dict:
    """Westfeld-Pfitzmann chi-square on pairs of values (2k, 2k+1).

    p_value is the probability, under the hypothesis "pairs are equalised as after full
    LSB replacement", of observing a statistic at least this large. High p_value => pairs
    are equalised (consistent with embedding but ALSO with noisy natural images).
    Low p_value => pairs clearly unequal => argues against dense LSB embedding.
    """
    hist = np.bincount(samples.astype(np.int64), minlength=256).astype(np.float64)
    even, odd = hist[0::2], hist[1::2]
    expected = (even + odd) / 2.0
    mask = expected >= 5
    k = int(mask.sum())
    if k < 8:
        return {"valid": False, "usable_bins": k, "reason": "Too few populated value pairs for a reliable test."}
    stat = float((((even[mask] - expected[mask]) ** 2) / expected[mask]).sum())
    return {"valid": True, "usable_bins": k, "statistic": round(stat, 3), "p_value": float(chi2.sf(stat, k - 1))}


def chi_square_windows(rgb: np.ndarray) -> list:
    """Run the test on growing prefixes of the embedding order (row-major, RGB-interleaved)."""
    flat = rgb.reshape(-1)
    n = flat.size
    sizes = sorted({min(n, s) for s in (16384, 65536, 262144, n)})
    out = []
    for s in sizes:
        r = chi_square_pov(flat[:s])
        r["samples"] = int(s)
        r["pixels_equivalent"] = int(s // 3)
        if r.get("p_value") is not None:
            r["p_value"] = round(r["p_value"], 6)
        out.append(r)
    return out


# --- RS analysis (Fridrich, Goljan, Du 2001) -------------------------------------------
_MASK = np.array([0, 1, 1, 0])


def _discr(g: np.ndarray) -> np.ndarray:
    return np.abs(np.diff(g, axis=1)).sum(axis=1)


def _flip(g: np.ndarray, mask: np.ndarray) -> np.ndarray:
    g = g.copy()
    for i, m in enumerate(mask):
        if m == 1:
            g[:, i] = g[:, i] ^ 1
        elif m == -1:
            g[:, i] = ((g[:, i] + 1) ^ 1) - 1
    return g


def _rs_counts(groups: np.ndarray, mask: np.ndarray):
    d0 = _discr(groups)
    d1 = _discr(_flip(groups, mask))
    return int((d1 > d0).sum()), int((d1 < d0).sum())


def rs_channel(ch: np.ndarray) -> dict:
    h, w = ch.shape
    w4 = (w // 4) * 4
    groups = ch[:, :w4].astype(np.int16).reshape(-1, 4)
    n = groups.shape[0]
    if n < 500:
        return {"valid": False, "reason": "Image too small for RS analysis."}
    flipped = groups ^ 1
    rm, sm = _rs_counts(groups, _MASK)
    rnm, snm = _rs_counts(groups, -_MASK)
    rm1, sm1 = _rs_counts(flipped, _MASK)
    rnm1, snm1 = _rs_counts(flipped, -_MASK)
    d0, d1 = (rm - sm) / n, (rm1 - sm1) / n
    dn0, dn1 = (rnm - snm) / n, (rnm1 - snm1) / n
    a = 2 * (d1 + d0)
    b = dn0 - dn1 - d1 - 3 * d0
    c = d0 - dn0
    if abs(a) < 1e-12:
        if abs(b) < 1e-12:
            return {"valid": False, "reason": "RS equation degenerate."}
        x = -c / b
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return {"valid": False, "reason": "RS equation has no real solution (image unsuited to RS analysis)."}
        r1, r2 = (-b + disc ** 0.5) / (2 * a), (-b - disc ** 0.5) / (2 * a)
        x = r1 if abs(r1) < abs(r2) else r2
    denom = x - 0.5
    if abs(denom) < 1e-12:
        return {"valid": False, "reason": "RS estimate unstable."}
    p = x / denom
    return {"valid": True, "estimated_payload_fraction": round(float(min(max(p, 0.0), 1.0)), 4),
            "raw_estimate": round(float(p), 4),
            "counts": {"R_M": rm, "S_M": sm, "R_-M": rnm, "S_-M": snm, "groups": n}}


def rs_analysis(rgb: np.ndarray) -> dict:
    per = {n: rs_channel(rgb[:, :, i]) for i, n in enumerate(CHANNELS)}
    vals = [v["estimated_payload_fraction"] for v in per.values() if v.get("valid")]
    return {"channels": per, "valid": bool(vals),
            "mean_estimated_payload_fraction": round(float(np.mean(vals)), 4) if vals else None}


def header_probe(rgb: np.ndarray) -> dict:
    return parse_header(rgb)


def analyze_lsb(rgb: np.ndarray) -> dict:
    return {
        "bit_statistics": lsb_statistics(rgb),
        "chi_square_windows": chi_square_windows(rgb),
        "rs_analysis": rs_analysis(rgb),
        "custom_header_probe": header_probe(rgb),
    }


def lsb_visualization_png(rgb: np.ndarray, max_side: int = 768) -> bytes:
    """Amplified LSB plane (each channel's LSB mapped to 0/255). This is a FORENSIC VIEW of
    the bit-plane -- it is not a decoded or recovered image."""
    plane = ((rgb & 1) * 255).astype(np.uint8)
    img = Image.fromarray(plane, "RGB")
    scale = max(img.size) / max_side
    if scale > 1:
        img = img.resize((max(1, int(img.width / scale)), max(1, int(img.height / scale))), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
