"""Deterministic synthetic images for the demo mode and for tests."""
import io

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter


def make_demo_carrier(size: int = 512, seed: int = 7, noise_sigma: float = 2.5) -> Image.Image:
    """A photo-like synthetic carrier: smooth structure + sensor-style noise."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64) / size
    chans = []
    for k in range(3):
        base = 90 + 80 * np.sin(2 * np.pi * (xx * (1 + k) * 0.7 + yy * 0.5 + k / 3.0))
        base += 40 * gaussian_filter(rng.normal(size=(size, size)), size / 12) * (size / 12) / 2
        base += rng.normal(0, noise_sigma, size=(size, size))
        chans.append(base)
    arr = np.clip(np.stack(chans, axis=-1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def make_demo_secret(size: int = 64, label: str = "SECRET") -> bytes:
    """A small, compressible PNG used as the default hidden image."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            px[x, y] = (int(255 * x / size), int(255 * y / size), 160)
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, size - 5, size - 5], outline=(255, 255, 255))
    draw.text((10, size // 2 - 5), label[:8], fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
