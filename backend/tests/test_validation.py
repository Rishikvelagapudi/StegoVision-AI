import io

import pytest
from PIL import Image

from app.config import get_settings
from app.core.validation import validate_image
from app.errors import ValidationError
from tests.helpers import bmp_bytes, carrier, env, jpeg_bytes, png_bytes


def _code(data):
    with pytest.raises(ValidationError) as e:
        validate_image(data, get_settings())
    return e.value.code, e.value.status


def test_valid_png_jpeg_bmp():
    img = carrier(size=64)
    for fmt, blob in (("PNG", png_bytes(img)), ("JPEG", jpeg_bytes(img)), ("BMP", bmp_bytes(img))):
        v = validate_image(blob, get_settings())
        assert v.format == fmt and (v.width, v.height) == (64, 64)


def test_empty_file():
    assert _code(b"") == ("empty_file", 400)


def test_unsupported_format_by_content_not_extension():
    assert _code(b"GIF89a" + b"\x00" * 100)[0] == "unsupported_format"
    assert _code(b"MZ\x90\x00" + b"\x00" * 200)[0] == "unsupported_format"
    assert _code(b"just some text pretending to be photo.png")[0] == "unsupported_format"
    buf = io.BytesIO()
    carrier(size=64).save(buf, format="WEBP")
    assert _code(buf.getvalue())[0] == "unsupported_format"


def test_truncated_png_is_corrupted():
    blob = png_bytes(carrier(size=128))
    assert _code(blob[: len(blob) // 2])[0] == "corrupted_image"


def test_garbage_after_valid_signature():
    assert _code(b"\x89PNG\r\n\x1a\n" + b"garbage" * 50)[0] == "corrupted_image"


def test_corrupted_idat_crc():
    blob = bytearray(png_bytes(carrier(size=64)))
    i = blob.find(b"IDAT") + 10
    blob[i] ^= 0xFF
    assert _code(bytes(blob))[0] == "corrupted_image"


def test_size_limit():
    with env(MAX_UPLOAD_MB=1):
        assert _code(b"\x89PNG\r\n\x1a\n" + b"0" * (1024 * 1024 + 1)) == ("file_too_large", 413)


def test_dimension_limit_and_minimum():
    with env(MAX_DIMENSION=100):
        assert _code(png_bytes(carrier(size=128)))[0] == "image_too_large"
    tiny = Image.new("RGB", (4, 4))
    assert _code(png_bytes(tiny))[0] == "image_too_small"
