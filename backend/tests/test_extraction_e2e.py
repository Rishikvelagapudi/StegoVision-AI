"""End-to-end tests through the service layer (the same code the REST endpoints call)."""
import hashlib
import io
import json

import numpy as np
import pytest
from PIL import Image

from app import service
from app.core import stego_format as sf
from app.errors import AppError, NotFoundError, ValidationError
from tests.helpers import carrier, jpeg_bytes, png_bytes, secret_png


def test_e2e_embed_upload_analyze_extract_bytes_match():
    secret = secret_png()
    car = carrier(seed=9, size=300)
    carrier_before = png_bytes(car)
    stego = sf.encode_to_png_bytes(car, secret, sf.TYPE_PNG)
    assert png_bytes(car) == carrier_before  # carrier preserved

    rec = service.analyze("stego.png", stego)
    assert rec["detection"]["outcome"] == "Possible Steganography Detected"
    assert rec["extraction"]["status"] == "not_attempted"  # detection and extraction are separate

    ext = service.extract(rec["analysis_id"])
    assert ext["extraction"]["status"] == "success"
    info = ext["extraction"]["recovered"]
    assert info["kind"] == "image" and info["format"] == "PNG" and (info["width"], info["height"]) == (48, 48)
    assert info["sha256"] == hashlib.sha256(secret).hexdigest()

    blob, mime, name = service.get_recovered(rec["analysis_id"])
    assert blob == secret and mime == "image/png" and name == "recovered_image.png"
    Image.open(io.BytesIO(blob)).verify()


def test_hidden_text_extraction():
    st = sf.encode_to_png_bytes(carrier(), "launch code: 0451 ✓".encode(), sf.TYPE_TEXT)
    rec = service.analyze("t.png", st)
    ext = service.extract(rec["analysis_id"])["extraction"]
    assert ext["status"] == "success" and ext["recovered"]["kind"] == "text"
    assert ext["recovered"]["text_preview"] == "launch code: 0451 ✓"
    blob, mime, name = service.get_recovered(rec["analysis_id"])
    assert blob.decode() == "launch code: 0451 ✓" and name.endswith(".txt")


def test_clean_image_extraction_fails_with_explanation():
    rec = service.analyze("c.png", png_bytes(carrier(seed=21)))
    ext = service.extract(rec["analysis_id"])["extraction"]
    assert ext["status"] == "failed" and ext["recovered"] is None
    assert ext["possible_reasons"]
    assert {a["method"] for a in ext["methods_attempted"]} >= {"lsb_custom_svai_v1", "trailing_appended_png"}
    with pytest.raises(AppError) as e:
        service.get_recovered(rec["analysis_id"])
    assert e.value.status == 404 and e.value.code == "no_recovered_payload"


def test_corrupted_payload_reports_failure_not_fake_image():
    arr = np.array(sf.embed(carrier(), secret_png(), sf.TYPE_PNG))
    arr.reshape(-1)[sf.HEADER_BITS + 100] ^= 1
    rec = service.analyze("bad.png", png_bytes(Image.fromarray(arr, "RGB")))
    ext = service.extract(rec["analysis_id"])["extraction"]
    assert ext["status"] == "failed"
    lsb = [a for a in ext["methods_attempted"] if a["method"] == "lsb_custom_svai_v1"][0]
    assert lsb["reason_code"] == "crc_mismatch"


def test_payload_with_valid_crc_but_invalid_png_is_rejected():
    fake = b"\x89PNG\r\n\x1a\n" + b"this is not a real png"
    st = sf.encode_to_png_bytes(carrier(), fake, sf.TYPE_PNG)
    rec = service.analyze("f.png", st)
    ext = service.extract(rec["analysis_id"])["extraction"]
    assert ext["status"] == "failed"
    lsb = [a for a in ext["methods_attempted"] if a["method"] == "lsb_custom_svai_v1"][0]
    assert lsb["reason_code"] == "payload_invalid_image"


def test_appended_png_extraction():
    secret = secret_png()
    rec = service.analyze("a.png", png_bytes(carrier()) + secret)
    ext = service.extract(rec["analysis_id"])["extraction"]
    assert ext["status"] == "success" and ext["recovered"]["method"] == "trailing_appended_png"
    assert service.get_recovered(rec["analysis_id"])[0] == secret


def test_jpeg_extraction_fails_gracefully():
    rec = service.analyze("j.jpg", jpeg_bytes(carrier(size=128)))
    assert service.extract(rec["analysis_id"])["extraction"]["status"] == "failed"


def test_invalid_uploads_rejected_by_service():
    for blob, code in ((b"", "empty_file"), (b"not an image", "unsupported_format"),
                       (png_bytes(carrier(size=64))[:80], "corrupted_image")):
        with pytest.raises(ValidationError) as e:
            service.analyze("x.png", blob)
        assert e.value.code == code


def test_unknown_and_malicious_ids_are_404():
    for bad in ("0" * 32, "../../etc/passwd", "..%2f..%2fetc%2fpasswd", "", "G" * 32):
        with pytest.raises(NotFoundError):
            service.get_analysis(bad)
        with pytest.raises(NotFoundError):
            service.get_original(bad)


def test_filename_is_sanitised():
    rec = service.analyze("../../etc/pass<wd>\x00.png", png_bytes(carrier(size=64)))
    assert "/" not in rec["filename"] and "\\" not in rec["filename"]
    assert "<" not in rec["filename"] and ">" not in rec["filename"] and "\x00" not in rec["filename"]
    assert rec["filename"] == "pass_wd__.png"


def test_encode_test_image_demo_and_validation():
    out, info = service.encode_test_image(None, None, None)
    assert info["demo_carrier"] and info["demo_payload"] and out.startswith(b"\x89PNG")
    rec = service.analyze("demo.png", out)
    assert service.extract(rec["analysis_id"])["extraction"]["status"] == "success"
    with pytest.raises(ValidationError):
        service.encode_test_image(None, b"not a png", None)
    with pytest.raises(ValidationError):
        service.encode_test_image(None, secret_png(), "also text")
    with pytest.raises(AppError) as e:
        service.encode_test_image(png_bytes(carrier(size=32)), None, "x" * 5000)
    assert e.value.code == "payload_too_large"


def test_result_expiry():
    from tests.helpers import env
    service.reset_store()
    with env(RESULT_TTL_SECONDS=0):
        service.reset_store()
        rec = service.analyze("e.png", png_bytes(carrier(size=64)))
        import time
        time.sleep(0.05)
        with pytest.raises(NotFoundError):
            service.get_analysis(rec["analysis_id"])
    service.reset_store()


def test_concurrent_requests_do_not_mix_results():
    from concurrent.futures import ThreadPoolExecutor

    def work(i):
        text = f"message-{i}-" + "x" * i
        st = sf.encode_to_png_bytes(carrier(seed=i, size=128), text.encode(), sf.TYPE_TEXT)
        rec = service.analyze(f"f{i}.png", st)
        service.extract(rec["analysis_id"])
        return text, service.get_recovered(rec["analysis_id"])[0].decode()

    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(work, range(16)))
    assert all(sent == got for sent, got in results)
