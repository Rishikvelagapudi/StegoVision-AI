"""Metadata and container-structure inspection. Everything here is MEASURED from the file;
`observations` are neutral notes -- none of them proves steganography."""
import math
import struct

from PIL import ExifTags

from .validation import sniff_format

TRAILER_MAGICS = (
    (b"\x89PNG\r\n\x1a\n", "PNG image"),
    (b"\xff\xd8\xff", "JPEG image"),
    (b"PK\x03\x04", "ZIP archive"),
    (b"Rar!", "RAR archive"),
    (b"7z\xbc\xaf\x27\x1c", "7-Zip archive"),
    (b"%PDF", "PDF document"),
    (b"\x1f\x8b", "GZIP data"),
    (b"GIF8", "GIF image"),
    (b"BM", "BMP image"),
    (b"MZ", "Windows executable (not executed)"),
    (b"\x7fELF", "ELF executable (not executed)"),
)


def shannon_entropy_bytes(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in counts if c)


def identify_trailer(trailer: bytes):
    for magic, name in TRAILER_MAGICS:
        if trailer.startswith(magic):
            return name
    return None


def find_trailing_data(data: bytes, fmt: str):
    """Return (offset, trailing_bytes) for bytes after the logical end of the image, or (None, b'')."""
    if fmt == "PNG":
        pos = 8
        while pos + 12 <= len(data):
            length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
            end = pos + 12 + length
            if ctype == b"IEND":
                return (end, data[end:]) if end < len(data) else (None, b"")
            pos = end
        return None, b""
    if fmt == "JPEG":
        idx = data.rfind(b"\xff\xd9")
        if idx != -1 and idx + 2 < len(data):
            return idx + 2, data[idx + 2:]
        return None, b""
    if fmt == "BMP" and len(data) >= 6:
        declared = struct.unpack("<I", data[2:6])[0]
        if 0 < declared < len(data):
            return declared, data[declared:]
    return None, b""


def png_chunks(data: bytes):
    chunks, pos = [], 8
    while pos + 12 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        name = ctype.decode("latin-1")
        chunks.append({"type": name, "length": length})
        pos += 12 + length
        if ctype == b"IEND":
            break
    return chunks


def _clip(v, n=160):
    s = v if isinstance(v, str) else repr(v)
    s = "".join(ch if ch.isprintable() else "?" for ch in s)
    return s if len(s) <= n else s[:n] + "…"


def analyze_metadata(data: bytes, img, fmt: str) -> dict:
    observations = []
    out = {"measured": {}, "observations": observations}
    m = out["measured"]
    m["declared_format"] = fmt
    m["sniffed_format"] = sniff_format(data)
    m["color_mode"] = img.mode

    # EXIF
    exif = {}
    try:
        for tag, val in img.getexif().items():
            if tag in (0x927C, 0x8769, 0x8825):  # MakerNote / sub-IFD pointers: skip raw blobs
                exif[ExifTags.TAGS.get(tag, str(tag))] = "<present>"
                continue
            exif[ExifTags.TAGS.get(tag, str(tag))] = _clip(val)
    except Exception:
        pass
    m["exif"] = dict(list(exif.items())[:40])
    m["exif_field_count"] = len(exif)

    # Textual metadata (PNG tEXt/iTXt, JPEG comments, etc.)
    text_items = {}
    for k, v in (img.info or {}).items():
        if isinstance(v, (str, bytes)) and k not in ("icc_profile", "exif"):
            text_items[_clip(k, 60)] = _clip(v.decode("latin-1") if isinstance(v, bytes) else v)
    m["text_fields"] = dict(list(text_items.items())[:30])
    m["has_icc_profile"] = "icc_profile" in (img.info or {})

    # Container structure
    if fmt == "PNG":
        chunks = png_chunks(data)
        m["png_chunks"] = chunks[:200]
        m["png_chunk_count"] = len(chunks)
        nonstandard = [c["type"] for c in chunks
                       if c["type"][0].islower() and c["type"][1].isupper()]  # private ancillary
        m["png_private_ancillary_chunks"] = nonstandard
        if nonstandard:
            observations.append({"severity": "notable", "message":
                f"Private ancillary PNG chunk(s) present: {', '.join(sorted(set(nonstandard)))}. "
                "Some tools store custom data this way, but many editors do too."})
        big_text = [c for c in chunks if c["type"] in ("tEXt", "zTXt", "iTXt") and c["length"] > 1024]
        if big_text:
            observations.append({"severity": "notable", "message":
                f"{len(big_text)} large text chunk(s) (>1 KiB). Large text metadata is unusual but not proof of hidden data."})

    offset, trailer = find_trailing_data(data, fmt)
    m["trailing_data_bytes"] = len(trailer)
    if trailer:
        kind = identify_trailer(trailer)
        m["trailing_data_offset"] = offset
        m["trailing_data_type"] = kind
        m["trailing_data_entropy"] = round(shannon_entropy_bytes(trailer[:1_000_000]), 4)
        msg = f"{len(trailer)} byte(s) follow the logical end of the image at offset {offset}."
        if kind:
            msg += f" The data begins with a {kind} signature."
        observations.append({"severity": "notable", "message": msg + " Appended data is a known hiding technique but also occurs with some editors/cameras."})
    else:
        m["trailing_data_type"] = None

    if fmt == "JPEG" and not exif:
        observations.append({"severity": "info", "message": "No EXIF metadata. This is common for images processed by social networks or editors."})
    if m["exif"].get("Software"):
        observations.append({"severity": "info", "message": f"Software tag: {m['exif']['Software']}."})
    if not observations:
        observations.append({"severity": "info", "message": "No metadata or container anomalies observed."})
    return out
