"""Validation of recovered payloads. Payloads are only ever parsed as data -- never executed."""
import hashlib
import io

from PIL import Image

from ..config import Settings
from ..errors import AppError
from .stego_format import TYPE_PNG, TYPE_TEXT

TYPE_PNG = 2
TYPE_TEXT = 1
TYPE_IMAGE = 3

PNG_SIG = b"\x89PNG\r\n\x1a\n"


class PayloadError(AppError):
    def __init__(self, code: str, message: str):
        super().__init__(code, message, 422)


def validate_image_payload(data: bytes, settings: Settings, expected_fmt: str = None) -> dict:
    Image.MAX_IMAGE_PIXELS = settings.max_pixels
    try:
        probe = Image.open(io.BytesIO(data))
        w, h = probe.size
        if w * h > settings.max_pixels:
            raise PayloadError("payload_too_large", "Recovered image has too many pixels.")
        Image.open(io.BytesIO(data)).verify()
        img = Image.open(io.BytesIO(data))
        img.load()
    except PayloadError:
        raise
    except Exception as exc:
        raise PayloadError("payload_invalid_image", f"Recovered bytes are not a valid image: {exc}")
    
    fmt = img.format or "PNG"
    if expected_fmt and fmt != expected_fmt:
        raise PayloadError("payload_not_png" if expected_fmt == "PNG" else "payload_wrong_format",
                           f"Recovered image is not in {expected_fmt} format.")
    
    ext_map = {"PNG": "png", "JPEG": "jpg", "BMP": "bmp", "GIF": "gif", "WEBP": "webp"}
    ext = ext_map.get(fmt, "png")
    mime_map = {"PNG": "image/png", "JPEG": "image/jpeg", "BMP": "image/bmp", "GIF": "image/gif", "WEBP": "image/webp"}
    mime = mime_map.get(fmt, "image/png")
    
    return {
        "kind": "image",
        "format": fmt,
        "mime_type": mime,
        "filename": f"recovered_image.{ext}",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
    }


def validate_png(data: bytes, settings: Settings) -> dict:
    if not data.startswith(PNG_SIG):
        raise PayloadError("payload_not_png", "Recovered bytes do not start with a PNG signature.")
    return validate_image_payload(data, settings, expected_fmt="PNG")


def validate_text(data: bytes, settings: Settings) -> dict:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise PayloadError("payload_not_text", "Recovered bytes are not valid UTF-8 text.")
    if not text:
        raise PayloadError("payload_empty", "Recovered text is empty.")
    printable = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
    if printable / len(text) < 0.95:
        raise PayloadError("payload_not_text", "Recovered text contains too many control characters.")
    return {
        "kind": "text",
        "format": "UTF-8 text",
        "mime_type": "text/plain; charset=utf-8",
        "filename": "recovered_message.txt",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "char_count": len(text),
        "text_preview": text[:4000],
        "truncated": len(text) > 4000,
    }


def validate_payload(type_id: int, data: bytes, settings: Settings) -> dict:
    if type_id == TYPE_PNG:
        return validate_png(data, settings)
    if type_id == TYPE_TEXT:
        return validate_text(data, settings)
    if type_id == TYPE_IMAGE:
        return validate_image_payload(data, settings)
    raise PayloadError("unsupported_payload_type", "Unsupported payload type.")
