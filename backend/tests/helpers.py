import io
import os
from contextlib import contextmanager

import numpy as np
from PIL import Image

from app.core import demo


def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def jpeg_bytes(img: Image.Image, quality=90) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def bmp_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="BMP")
    return buf.getvalue()


def carrier(seed=3, size=256):
    return demo.make_demo_carrier(size, seed=seed)


def secret_png(size=48, color=(200, 30, 90)):
    """A secret image with non-trivial content so byte-equality is a meaningful check."""
    rng = np.random.default_rng(5)
    arr = rng.integers(0, 255, (size, size, 3), dtype=np.uint8)
    arr[: size // 2] = color
    return png_bytes(Image.fromarray(arr, "RGB"))


def random_lsb_overwrite(img: Image.Image, fraction: float, seed=0) -> Image.Image:
    """Overwrite the LSBs of the first `fraction` of samples with random bits (no SVAI header)."""
    arr = np.array(img.convert("RGB"))
    flat = arr.reshape(-1)
    n = int(flat.size * fraction)
    bits = np.random.default_rng(seed).integers(0, 2, n, dtype=np.uint8)
    flat[:n] = (flat[:n] & 0xFE) | bits
    return Image.fromarray(flat.reshape(arr.shape), "RGB")


@contextmanager
def env(**kwargs):
    old = {k: os.environ.get(k) for k in kwargs}
    os.environ.update({k: str(v) for k, v in kwargs.items()})
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
