"""Optional PyTorch steganalysis classifier -- the integration point for a TRAINED model.

No weights ship with this repository. Unless STEGO_MODEL_PATH points to a compatible
checkpoint AND torch is installed, the classifier reports itself as unavailable and
NO prediction or confidence is produced (nothing is invented).

Checkpoint format (torch.save):
    {"state_dict": <StegoCNN state dict>, "meta": {"labels": ["cover", "stego"], "patch": 128, "notes": "..."}}
or a bare state_dict of `StegoCNN`. Output class index 1 is interpreted as "stego".
To plug in a different architecture, subclass/replace `load_classifier()`.
"""
import os
import threading

import numpy as np

_lock = threading.Lock()
_cache = {}


def _build_model(torch):
    nn = torch.nn

    class StegoCNN(nn.Module):
        """Small residual-domain CNN: fixed high-pass filter -> conv stack -> 2-way logits."""

        def __init__(self):
            super().__init__()
            kv = torch.tensor([[-1, 2, -2, 2, -1], [2, -6, 8, -6, 2], [-2, 8, -12, 8, -2],
                               [2, -6, 8, -6, 2], [-1, 2, -2, 2, -1]], dtype=torch.float32) / 12.0
            self.register_buffer("hp", kv.view(1, 1, 5, 5))
            def blk(i, o):
                return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.AvgPool2d(2))
            self.features = nn.Sequential(blk(1, 16), blk(16, 32), blk(32, 64), blk(64, 128))
            self.head = nn.Linear(128, 2)

        def forward(self, x):  # x: (N,1,H,W) in [0,255]
            x = torch.nn.functional.conv2d(x, self.hp, padding=2).clamp(-3, 3)
            x = self.features(x)
            return self.head(x.mean(dim=(2, 3)))

    return StegoCNN()


def load_classifier(model_path: str):
    """Return a predictor callable(rgb_array)->dict, or (None, reason)."""
    if not model_path:
        return None, "No trained model configured (STEGO_MODEL_PATH is not set)."
    if not os.path.isfile(model_path):
        return None, "Configured model file was not found."
    try:
        import torch  # noqa: WPS433 (optional dependency)
    except ImportError:
        return None, "PyTorch is not installed; install requirements-ml.txt to enable AI classification."
    try:
        ckpt = torch.load(model_path, map_location="cpu", weights_only=True)
        meta = ckpt.get("meta", {}) if isinstance(ckpt, dict) else {}
        sd = ckpt["state_dict"] if isinstance(ckpt, dict) and "state_dict" in ckpt else ckpt
        model = _build_model(torch)
        model.load_state_dict(sd)
        model.eval()
    except Exception as exc:
        return None, f"Model could not be loaded: {exc}"
    patch = int(meta.get("patch", 128))

    def predict(rgb: np.ndarray) -> dict:
        gray = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]).astype(np.float32)
        h, w = gray.shape
        if h < patch or w < patch:
            raise ValueError(f"Image smaller than model patch size ({patch}px).")
        patches = [gray[y:y + patch, x:x + patch] for y in range(0, h - patch + 1, patch)
                   for x in range(0, w - patch + 1, patch)][:64]
        with torch.no_grad():
            logits = model(torch.from_numpy(np.stack(patches))[:, None])
            probs = torch.softmax(logits, dim=1)[:, 1]
        return {"stego_probability": float(probs.mean()), "patches_evaluated": len(patches),
                "model_notes": meta.get("notes", "")}

    return predict, None


def run_model(rgb: np.ndarray, model_path: str) -> dict:
    with _lock:
        if model_path not in _cache:
            _cache[model_path] = load_classifier(model_path)
        predictor, reason = _cache[model_path]
    if predictor is None:
        return {"available": False, "prediction": None, "confidence": None, "reason": reason}
    try:
        res = predictor(rgb)
    except Exception as exc:
        return {"available": False, "prediction": None, "confidence": None, "reason": f"Model inference failed: {exc}"}
    p = res["stego_probability"]
    return {"available": True, "prediction": "stego" if p >= 0.5 else "cover",
            "confidence": round(p if p >= 0.5 else 1 - p, 4), "stego_probability": round(p, 4),
            "patches_evaluated": res["patches_evaluated"], "reason": None,
            "note": "Model output is a statistical prediction, not proof; accuracy depends on its training data."}


def is_available(model_path: str) -> bool:
    """True only if a trained model is configured, loadable and torch is installed."""
    if not model_path:
        return False
    with _lock:
        if model_path not in _cache:
            _cache[model_path] = load_classifier(model_path)
        return _cache[model_path][0] is not None
