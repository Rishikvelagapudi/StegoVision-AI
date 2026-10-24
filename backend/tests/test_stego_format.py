import io
import struct
import zlib

import numpy as np
import pytest
from PIL import Image

from app.config import get_settings
from app.core import stego_format as sf
from app.core.validation import rgb_array
from tests.helpers import carrier, png_bytes, secret_png

MAXP = get_settings().max_payload_bytes


def _roundtrip(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    img.load()
    return sf.extract_from_image(img, MAXP)


def test_text_roundtrip_unicode():
    msg = "Hidden message ✓ — héllo".encode("utf-8")
    out = sf.encode_to_png_bytes(carrier(), msg, sf.TYPE_TEXT)
    p = _roundtrip(out)
    assert p.type_name == "text" and p.data == msg


def test_image_roundtrip_is_byte_exact():
    secret = secret_png()
    out = sf.encode_to_png_bytes(carrier(), secret, sf.TYPE_PNG)
    p = _roundtrip(out)
    assert p.type_name == "png" and p.data == secret


def test_carrier_is_preserved_and_only_lsbs_change():
    car = carrier()
    before = np.array(car).copy()
    out = sf.embed(car, b"x" * 500, sf.TYPE_TEXT)
    assert np.array_equal(before, np.array(car))  # input object untouched
    diff = np.abs(np.array(out).astype(int) - before.astype(int))
    assert diff.max() <= 1


def test_alpha_channel_untouched():
    rgba = Image.fromarray(np.dstack([np.array(carrier(size=64)), np.full((64, 64), 77, np.uint8)]), "RGBA")
    out = sf.embed(rgba, b"hello", sf.TYPE_TEXT)
    assert out.mode == "RGBA" and (np.array(out)[:, :, 3] == 77).all()
    assert sf.extract_from_image(out, MAXP).data == b"hello"


def test_payload_too_large_rejected():
    small = carrier(size=32)
    with pytest.raises(sf.StegoFormatError) as e:
        sf.embed(small, b"a" * sf.capacity_bytes(32, 32) + b"b", sf.TYPE_TEXT)
    assert e.value.code == "payload_too_large"


def test_capacity_exact_fit():
    small = carrier(size=32)
    cap = sf.capacity_bytes(32, 32)
    out = sf.embed(small, b"z" * cap, sf.TYPE_TEXT)
    assert len(sf.extract_from_image(out, MAXP).data) == cap


def test_clean_image_has_no_signature():
    with pytest.raises(sf.StegoFormatError) as e:
        sf.extract(rgb_array(carrier()), MAXP)
    assert e.value.code == "signature_not_found"


def test_corrupted_payload_detected_by_crc():
    out = sf.embed(carrier(), b"A secret that must not be silently corrupted", sf.TYPE_TEXT)
    arr = np.array(out)
    flat = arr.reshape(-1)
    flat[sf.HEADER_BITS + 5] ^= 1  # flip one payload bit
    with pytest.raises(sf.StegoFormatError) as e:
        sf.extract(arr[:, :, :3], MAXP)
    assert e.value.code == "crc_mismatch"


def _write_raw_blob(blob: bytes, size=64):
    arr = np.array(carrier(size=size))
    flat = arr.reshape(-1)
    bits = np.unpackbits(np.frombuffer(blob, dtype=np.uint8))
    flat[: len(bits)] = (flat[: len(bits)] & 0xFE) | bits
    return flat.reshape(arr.shape)


def test_invalid_length_in_header():
    blob = sf.HEADER.pack(sf.MAGIC, 1, sf.TYPE_TEXT, 0, 10_000_000, 0)
    with pytest.raises(sf.StegoFormatError) as e:
        sf.extract(_write_raw_blob(blob), 10**9)
    assert e.value.code == "invalid_length"


def test_unsupported_version_and_type():
    with pytest.raises(sf.StegoFormatError) as e:
        sf.extract(_write_raw_blob(sf.HEADER.pack(sf.MAGIC, 9, sf.TYPE_TEXT, 0, 0, 0)), MAXP)
    assert e.value.code == "unsupported_version"
    with pytest.raises(sf.StegoFormatError) as e:
        sf.extract(_write_raw_blob(sf.HEADER.pack(sf.MAGIC, 1, 7, 0, 0, 0)), MAXP)
    assert e.value.code == "unsupported_payload_type"


def test_header_layout_is_documented_size():
    assert sf.HEADER.size == 15
    assert sf.capacity_bytes(100, 100) == (100 * 100 * 3) // 8 - 15
