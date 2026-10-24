"""Stand-alone encoder/decoder for the StegoVision custom LSB format (SVAI v1).

    python -m tools.stego_cli encode --carrier cover.png --secret-image secret.png --out stego.png
    python -m tools.stego_cli encode --carrier cover.png --secret-text "meet at dawn" --out stego.png
    python -m tools.stego_cli decode --image stego.png --out recovered      # extension added automatically

The carrier file is never modified; output is always a new lossless PNG.
"""
import argparse
import io
import sys

from PIL import Image

from app.config import get_settings
from app.core import stego_format as sf
from app.core.payload import validate_payload


def cmd_encode(a):
    carrier = Image.open(a.carrier)
    carrier.load()
    if bool(a.secret_image) == bool(a.secret_text):
        sys.exit("Provide exactly one of --secret-image or --secret-text")
    if a.secret_image:
        data, ptype = open(a.secret_image, "rb").read(), sf.TYPE_PNG
        validate_payload(ptype, data, get_settings())
    else:
        data, ptype = a.secret_text.encode("utf-8"), sf.TYPE_TEXT
    out = sf.encode_to_png_bytes(carrier, data, ptype)
    with open(a.out, "xb" if not a.force else "wb") as fh:
        fh.write(out)
    print(f"Wrote {a.out}: embedded {len(data)} bytes ({sf.TYPE_NAMES[ptype]}); "
          f"capacity {sf.capacity_bytes(*carrier.size)} bytes")


def cmd_decode(a):
    s = get_settings()
    img = Image.open(a.image)
    img.load()
    p = sf.extract_from_image(img, s.max_payload_bytes)
    info = validate_payload(p.type_id, p.data, s)
    path = a.out + (".png" if info["kind"] == "image" else ".txt")
    with open(path, "xb" if not a.force else "wb") as fh:
        fh.write(p.data)
    print(f"Recovered {info['kind']} ({info['size_bytes']} bytes, sha256 {info['sha256'][:16]}…) -> {path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("encode")
    e.add_argument("--carrier", required=True)
    e.add_argument("--secret-image")
    e.add_argument("--secret-text")
    e.add_argument("--out", required=True)
    e.add_argument("--force", action="store_true", help="overwrite output")
    e.set_defaults(fn=cmd_encode)
    d = sub.add_parser("decode")
    d.add_argument("--image", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--force", action="store_true")
    d.set_defaults(fn=cmd_decode)
    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except Exception as exc:  # user-facing CLI
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
