"""Pixel-statistics feature extraction. All numeric values are MEASURED; `interpretation`
strings are HEURISTIC and deliberately cautious."""
import cv2
import numpy as np


def entropy(values: np.ndarray, bins: int = 256) -> float:
    hist = np.bincount(values.reshape(-1).astype(np.int64), minlength=bins).astype(np.float64)
    p = hist[hist > 0] / hist.sum()
    return float(-(p * np.log2(p)).sum())


def adjacent_correlation(ch: np.ndarray) -> float:
    a = ch[:, :-1].astype(np.float64).ravel()
    b = ch[:, 1:].astype(np.float64).ravel()
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 1.0
    return float(np.corrcoef(a, b)[0, 1])


def analyze_statistics(rgb: np.ndarray) -> dict:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    names = ("red", "green", "blue")
    per = {}
    for i, n in enumerate(names):
        ch = rgb[:, :, i]
        per[n] = {
            "mean": round(float(ch.mean()), 3),
            "std": round(float(ch.std()), 3),
            "min": int(ch.min()),
            "max": int(ch.max()),
            "unique_values": int(np.unique(ch).size),
            "entropy_bits": round(entropy(ch), 4),
            "adjacent_pixel_correlation": round(adjacent_correlation(ch), 5),
        }
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    hist = np.bincount(gray.ravel(), minlength=256)
    measured = {
        "grayscale_entropy_bits": round(entropy(gray), 4),
        "max_possible_entropy_bits": 8.0,
        "laplacian_variance": round(float(lap.var()), 3),
        "saturated_pixel_fraction": round(float(((gray == 0) | (gray == 255)).mean()), 5),
        "unique_gray_levels": int((hist > 0).sum()),
        "channels": per,
        "histogram_gray": hist.astype(int).tolist(),
    }
    interp = []
    ge = measured["grayscale_entropy_bits"]
    if ge > 7.5:
        interp.append("High grayscale entropy (>7.5 bits). Common for photographs and noisy images; NOT evidence of hidden data on its own.")
    elif ge < 4:
        interp.append("Low entropy: image is graphic-like or flat. Statistical LSB tests are less informative on such images.")
    else:
        interp.append("Entropy is in a typical range for natural or synthetic images.")
    if measured["unique_gray_levels"] < 64:
        interp.append("Few distinct gray levels (possibly palettised, posterised or synthetic). LSB statistics may be unreliable.")
    if measured["laplacian_variance"] < 5:
        interp.append("Very smooth image (low Laplacian variance); random-looking LSB noise would stand out more here, but flat images also give uninformative tests.")
    return {"measured": measured, "interpretation": interp}
