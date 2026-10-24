"""Hidden-content extraction. Independent of detection; each method reports its own status.

Add a method by appending an entry to EXTRACTORS: fn(ctx) -> ParsedPayload-like tuple
(type_id, bytes) or raises AppError with a reason code.
"""
import io
import struct

import numpy as np
from PIL import Image

from ..config import Settings
from ..errors import AppError
from .metadata import find_trailing_data
from .payload import PNG_SIG, PayloadError, TYPE_IMAGE, validate_payload
from .stego_format import TYPE_PNG, TYPE_TEXT, StegoFormatError, extract as svai_extract
from .validation import rgb_array


def _lsb_svai(ctx):
    p = svai_extract(ctx["rgb"], ctx["settings"].max_payload_bytes)
    return p.type_id, p.data


def _trailing_png(ctx):
    _, trailer = find_trailing_data(ctx["data"], ctx["fmt"])
    if not trailer:
        raise StegoFormatError("no_trailing_data", "No data is appended after the image end.")
    start = trailer.find(PNG_SIG)
    if start != 0:
        raise StegoFormatError("no_appended_png", "Appended data does not start with a PNG signature.")
    return TYPE_PNG, trailer


def _trailing_image(ctx):
    _, trailer = find_trailing_data(ctx["data"], ctx["fmt"])
    if not trailer:
        raise StegoFormatError("no_trailing_data", "No data is appended after the image end.")
    if trailer.startswith(PNG_SIG):
        raise StegoFormatError("already_handled", "PNG trailer is handled by trailing_appended_png.")
    try:
        Image.open(io.BytesIO(trailer)).verify()
        return TYPE_IMAGE, trailer
    except Exception:
        raise StegoFormatError("no_trailing_image", "Appended data is not a recognizable image.")


def _lsb_raw_image(ctx):
    rgb = ctx["rgb"]
    flat_rgb = rgb.reshape(-1)
    flat_r = rgb[:, :, 0].reshape(-1)
    flat_g = rgb[:, :, 1].reshape(-1)
    flat_b = rgb[:, :, 2].reshape(-1)

    streams = [
        ("rgb_interleaved", np.packbits(flat_rgb & 1).tobytes()),
        ("red_plane", np.packbits(flat_r & 1).tobytes()),
        ("green_plane", np.packbits(flat_g & 1).tobytes()),
        ("blue_plane", np.packbits(flat_b & 1).tobytes()),
    ]

    for _, raw in streams:
        # Check for embedded PNG
        png_pos = raw.find(PNG_SIG)
        if png_pos != -1:
            iend_pos = raw.find(b"IEND\xaeB\x60\x82", png_pos)
            if iend_pos != -1:
                candidate = raw[png_pos : iend_pos + 8]
                try:
                    Image.open(io.BytesIO(candidate)).verify()
                    return TYPE_PNG, candidate
                except Exception:
                    pass

        # Check for embedded JPEG
        jpg_pos = raw.find(b"\xff\xd8\xff")
        if jpg_pos != -1:
            jpg_end = raw.find(b"\xff\xd9", jpg_pos)
            if jpg_end != -1 and (jpg_end - jpg_pos) > 100:
                candidate = raw[jpg_pos : jpg_end + 2]
                try:
                    Image.open(io.BytesIO(candidate)).verify()
                    return TYPE_IMAGE, candidate
                except Exception:
                    pass

        # Check for embedded BMP
        bmp_pos = raw.find(b"BM")
        if bmp_pos != -1 and bmp_pos + 6 <= len(raw):
            declared_sz = struct.unpack("<I", raw[bmp_pos + 2 : bmp_pos + 6])[0]
            if 100 < declared_sz <= len(raw) - bmp_pos:
                candidate = raw[bmp_pos : bmp_pos + declared_sz]
                try:
                    Image.open(io.BytesIO(candidate)).verify()
                    return TYPE_IMAGE, candidate
                except Exception:
                    pass

    raise StegoFormatError("no_raw_lsb_image", "No embedded PNG/JPEG/BMP image signature found in LSB streams.")


def _lsb_raw_text(ctx):
    rgb = ctx["rgb"]
    flat_rgb = rgb.reshape(-1)
    raw = np.packbits(flat_rgb & 1).tobytes()
    max_check = min(len(raw), 100000)

    # 1. Check length-prefixed text (4 bytes big-endian or little-endian)
    if len(raw) >= 5:
        be_len = struct.unpack(">I", raw[:4])[0]
        le_len = struct.unpack("<I", raw[:4])[0]
        for length in (be_len, le_len):
            if 4 <= length <= max_check - 4:
                candidate = raw[4 : 4 + length]
                try:
                    txt = candidate.decode("utf-8")
                    if len(txt) >= 4 and sum(1 for c in txt if c.isprintable() or c in "\n\r\t") / len(txt) > 0.95:
                        return TYPE_TEXT, candidate
                except UnicodeDecodeError:
                    pass

    # 2. Check null-terminated string at start
    null_pos = raw[:max_check].find(b"\x00")
    if null_pos > 8:
        candidate = raw[:null_pos]
        try:
            txt = candidate.decode("utf-8")
            if sum(1 for c in txt if c.isprintable() or c in "\n\r\t") / len(txt) > 0.95:
                return TYPE_TEXT, candidate
        except UnicodeDecodeError:
            pass

    raise StegoFormatError("no_raw_lsb_text", "No plain text found in LSB stream.")


EXTRACTORS = [
    ("lsb_custom_svai_v1", "StegoVision custom LSB format (SVAI v1), RGB LSB, row-major", _lsb_svai),
    ("trailing_appended_png", "PNG file appended after the image end marker", _trailing_png),
    ("trailing_appended_image", "Image file (JPEG/GIF/BMP/WebP) appended after image end", _trailing_image),
    ("lsb_embedded_image", "Raw image (PNG/JPEG/BMP) embedded in pixel LSB stream", _lsb_raw_image),
    ("lsb_embedded_text", "Plain text message embedded in pixel LSB stream", _lsb_raw_text),
]

FAILURE_REASONS = [
    "The image is clean (a false-positive detection).",
    "A different or unsupported embedding method/tool was used (only SVAI v1 and appended PNG are supported).",
    "A password/key or scattered-pixel order is required that this tool does not know.",
    "The stego image was re-compressed, resized or edited after embedding, destroying the payload.",
    "The embedded payload is corrupted or truncated.",
]


def run_extraction(data: bytes, fmt: str, img, settings: Settings) -> dict:
    ctx = {"data": data, "fmt": fmt, "rgb": rgb_array(img), "settings": settings}
    attempts, recovered = [], None
    for name, desc, fn in EXTRACTORS:
        entry = {"method": name, "description": desc, "status": "failed", "reason_code": None, "message": None}
        try:
            type_id, payload = fn(ctx)
            info = validate_payload(type_id, payload, settings)
            entry.update(status="success", message="Payload recovered and validated.")
            if recovered is None:
                recovered = {"info": info, "bytes": payload, "method": name}
        except (StegoFormatError, PayloadError, AppError) as exc:
            entry.update(reason_code=exc.code, message=exc.message)
        attempts.append(entry)
    result = {"status": "success" if recovered else "failed", "methods_attempted": attempts,
              "recovered": None, "possible_reasons": [] if recovered else list(FAILURE_REASONS)}
    if recovered:
        result["recovered"] = dict(recovered["info"], method=recovered["method"])
    return result, (recovered["bytes"] if recovered else None)
