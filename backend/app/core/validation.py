"""Image validation based on actual file contents (magic bytes + full decode)."""
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, UnidentifiedImageError

from ..config import Settings
from ..errors import ValidationError

SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"\xff\xd8\xff", "JPEG"),
    (b"BM", "BMP"),
)
SUPPORTED = ("PNG", "JPEG", "BMP")
LOSSLESS = ("PNG", "BMP")


def sniff_format(data: bytes):
    for sig, name in SIGNATURES:
        if data.startswith(sig):
            return name
    return None


@dataclass
class ValidatedImage:
    format: str
    width: int
    height: int
    mode: str
    image: Image.Image  # fully decoded


def validate_image(data: bytes, settings: Settings) -> ValidatedImage:
    if not data:
        raise ValidationError("empty_file", "The uploaded file is empty.", 400)
    if len(data) > settings.max_upload_bytes:
        mb = settings.max_upload_bytes // (1024 * 1024)
        raise ValidationError("file_too_large", f"File exceeds the {mb} MB upload limit.", 413)
    fmt = sniff_format(data)
    if fmt is None:
        raise ValidationError(
            "unsupported_format",
            "Unsupported or unrecognised file type. Supported formats: PNG, JPEG, BMP "
            "(determined from file contents, not the filename).",
            415,
        )
    Image.MAX_IMAGE_PIXELS = settings.max_pixels
    try:
        probe = Image.open(io.BytesIO(data))
        width, height = probe.size
    except Image.DecompressionBombError:
        raise ValidationError("image_too_large", "Image has too many pixels.", 413)
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise ValidationError("corrupted_image", f"The image header is malformed: {exc}", 422)
    if probe.format != fmt:
        raise ValidationError("format_mismatch", "File signature and image header disagree.", 422)
    if min(width, height) < settings.min_dimension:
        raise ValidationError("image_too_small", f"Image must be at least {settings.min_dimension}px per side.", 422)
    if max(width, height) > settings.max_dimension or width * height > settings.max_pixels:
        raise ValidationError(
            "image_too_large",
            f"Image dimensions {width}x{height} exceed limits "
            f"({settings.max_dimension}px per side, {settings.max_pixels:,} pixels).",
            413,
        )
    try:
        Image.open(io.BytesIO(data)).verify()
        img = Image.open(io.BytesIO(data))
        img.load()
    except Image.DecompressionBombError:
        raise ValidationError("image_too_large", "Image has too many pixels.", 413)
    except Exception as exc:  # truncated / corrupted pixel data
        raise ValidationError("corrupted_image", f"The image is corrupted or truncated: {exc}", 422)
    return ValidatedImage(fmt, width, height, img.mode, img)


def rgb_array(img: Image.Image) -> np.ndarray:
    """Return an (H, W, 3) uint8 array. Alpha is discarded; palette/gray expanded to RGB."""
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        return np.array(img)[:, :, :3].copy()
    if img.mode != "RGB":
        img = img.convert("RGB")
    return np.array(img).copy()
