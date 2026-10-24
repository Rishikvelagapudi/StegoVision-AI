"""StegoVision custom LSB format ("SVAI" v1) -- encoder and decoder.

THIS IS A PROJECT-SPECIFIC FORMAT. It is NOT compatible with OpenStego, Steghide,
OutGuess, F5, zsteg output, or any other third-party tool. StegoVision can only
decode images that were produced by this encoder (or an independent implementation
of the layout below).

Layout
------
* Carrier samples: the R, G, B channel values of every pixel, in row-major order,
  channel-interleaved (R0 G0 B0 R1 G1 B1 ...). An alpha channel, if present, is
  left untouched. Carrier must be stored losslessly (PNG output is always used).
* One payload bit is stored in the least-significant bit of each sample, MSB-first.
* The bit stream is: HEADER (15 bytes) || PAYLOAD (length bytes).

HEADER (big-endian, 15 bytes)
    4s  magic    b"SVAI"
    B   version  1
    B   type     1 = UTF-8 text, 2 = PNG image
    B   flags    0 (reserved)
    I   length   payload length in bytes
    I   crc32    CRC-32 of the payload
"""
import io
import struct
import zlib
from dataclasses import dataclass

import numpy as np
from PIL import Image

from ..errors import AppError
from .validation import rgb_array

MAGIC = b"SVAI"
VERSION = 1
TYPE_TEXT = 1
TYPE_PNG = 2
TYPE_NAMES = {TYPE_TEXT: "text", TYPE_PNG: "png"}
HEADER = struct.Struct(">4sBBBII")
HEADER_BITS = HEADER.size * 8


class StegoFormatError(AppError):
    """Raised for encode/decode failures. `code` identifies the failure reason."""

    def __init__(self, code: str, message: str, status: int = 422):
        super().__init__(code, message, status)


@dataclass
class ParsedPayload:
    type_id: int
    data: bytes
    version: int

    @property
    def type_name(self) -> str:
        return TYPE_NAMES[self.type_id]


def capacity_bytes(width: int, height: int) -> int:
    """Maximum payload size (excluding header) a width x height carrier can hold."""
    return max(0, (width * height * 3) // 8 - HEADER.size)


def build_blob(payload: bytes, type_id: int) -> bytes:
    if type_id not in TYPE_NAMES:
        raise StegoFormatError("unsupported_payload_type", "Payload type must be text or PNG.")
    return HEADER.pack(MAGIC, VERSION, type_id, 0, len(payload), zlib.crc32(payload) & 0xFFFFFFFF) + payload


def embed(carrier: Image.Image, payload: bytes, type_id: int) -> Image.Image:
    """Return a NEW image with the payload embedded. The carrier object is not modified."""
    blob = build_blob(payload, type_id)
    has_alpha = carrier.mode in ("RGBA", "LA", "PA") or (carrier.mode == "P" and "transparency" in carrier.info)
    base = carrier.convert("RGBA" if has_alpha else "RGB")
    arr = np.array(base)  # np.array copies -> carrier untouched
    w, h = base.size
    needed_bits = len(blob) * 8
    capacity_bits = w * h * 3
    if needed_bits > capacity_bits:
        raise StegoFormatError(
            "payload_too_large",
            f"Payload needs {len(blob)} bytes (incl. {HEADER.size}-byte header) but the "
            f"{w}x{h} carrier holds only {capacity_bits // 8} bytes.",
            413,
        )
    rgb = np.ascontiguousarray(arr[:, :, :3]).reshape(-1)
    bits = np.unpackbits(np.frombuffer(blob, dtype=np.uint8))
    rgb[:needed_bits] = (rgb[:needed_bits] & 0xFE) | bits
    arr[:, :, :3] = rgb.reshape(h, w, 3)
    return Image.fromarray(arr, "RGBA" if has_alpha else "RGB")


def encode_to_png_bytes(carrier_bytes_or_img, payload: bytes, type_id: int) -> bytes:
    img = carrier_bytes_or_img
    if isinstance(img, (bytes, bytearray)):
        img = Image.open(io.BytesIO(img))
        img.load()
    out = embed(img, payload, type_id)
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()


def _bits_to_bytes(samples: np.ndarray) -> bytes:
    return np.packbits(samples & 1).tobytes()


def parse_header(rgb: np.ndarray):
    """Try to read a header from an (H,W,3) array. Returns dict (valid flag + fields)."""
    flat = rgb.reshape(-1)
    total_bytes = flat.size // 8
    out = {"bits_available": int(flat.size), "signature_found": False}
    if total_bytes < HEADER.size:
        out["error"] = "image_too_small_for_header"
        return out
    raw = _bits_to_bytes(flat[:HEADER_BITS])
    magic, version, type_id, flags, length, crc = HEADER.unpack(raw)
    out["first_bytes_hex"] = raw[:8].hex()
    if magic != MAGIC:
        out["error"] = "signature_not_found"
        return out
    out.update(signature_found=True, version=version, type_id=type_id, flags=flags, length=length, crc32=crc)
    return out


def extract(rgb: np.ndarray, max_payload_bytes: int) -> ParsedPayload:
    """Decode an SVAI v1 payload from the LSBs of an (H,W,3) uint8 array."""
    hdr = parse_header(rgb)
    if not hdr["signature_found"]:
        if hdr.get("error") == "image_too_small_for_header":
            raise StegoFormatError("image_too_small", "Image is too small to contain a StegoVision header.")
        raise StegoFormatError(
            "signature_not_found",
            "No StegoVision (SVAI) signature found in the pixel LSBs. The image may be clean, "
            "or use a different/unsupported embedding method, a key, or lossy re-compression.",
        )
    if hdr["version"] != VERSION:
        raise StegoFormatError("unsupported_version", f"Unsupported SVAI version {hdr['version']}.")
    if hdr["type_id"] not in TYPE_NAMES:
        raise StegoFormatError("unsupported_payload_type", f"Unknown payload type id {hdr['type_id']}.")
    length = hdr["length"]
    flat = rgb.reshape(-1)
    available = flat.size // 8 - HEADER.size
    if length > available:
        raise StegoFormatError(
            "invalid_length",
            f"Header declares {length} payload bytes but the image can only hold {max(available, 0)}. "
            "The header or image is corrupted.",
        )
    if length > max_payload_bytes:
        raise StegoFormatError("payload_too_large", f"Declared payload ({length} bytes) exceeds the server limit.", 413)
    raw = _bits_to_bytes(flat[: (HEADER.size + length) * 8])
    payload = raw[HEADER.size:]
    if zlib.crc32(payload) & 0xFFFFFFFF != hdr["crc32"]:
        raise StegoFormatError("crc_mismatch", "Payload checksum mismatch: the embedded data is corrupted or was altered.")
    return ParsedPayload(hdr["type_id"], payload, hdr["version"])


def extract_from_image(img: Image.Image, max_payload_bytes: int) -> ParsedPayload:
    return extract(rgb_array(img), max_payload_bytes)
