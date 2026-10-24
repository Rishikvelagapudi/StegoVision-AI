"""Generate a set of test images into ./samples (git-ignored).

    python -m tools.make_test_images

Creates: carrier.png, secret.png, stego_image.png (hidden PNG), stego_text.png (hidden text),
clean.png (a different clean image), appended_png.png (PNG with a PNG appended), corrupted_stego.png.
"""
import os
import sys

import numpy as np
from PIL import Image

from app.core import demo
from app.core import stego_format as sf


def main(out="samples"):
    os.makedirs(out, exist_ok=True)
    carrier = demo.make_demo_carrier(512, seed=7)
    secret = demo.make_demo_secret(96, "SECRET")
    files = {
        "carrier.png": demo.to_png_bytes(carrier),
        "secret.png": secret,
        "stego_image.png": sf.encode_to_png_bytes(carrier, secret, sf.TYPE_PNG),
        "stego_text.png": sf.encode_to_png_bytes(carrier, "StegoVision test message ✓".encode(), sf.TYPE_TEXT),
        "clean.png": demo.to_png_bytes(demo.make_demo_carrier(512, seed=21)),
    }
    files["appended_png.png"] = files["carrier.png"] + secret
    arr = np.array(Image.open(__import__("io").BytesIO(files["stego_image.png"])))
    arr.reshape(-1)[sf.HEADER_BITS + 200] ^= 1  # flip one payload bit
    files["corrupted_stego.png"] = demo.to_png_bytes(Image.fromarray(arr, "RGB"))
    for name, blob in files.items():
        with open(os.path.join(out, name), "wb") as fh:
            fh.write(blob)
        print(f"wrote {os.path.join(out, name)} ({len(blob)} bytes)")


if __name__ == "__main__":
    main(*sys.argv[1:2])
