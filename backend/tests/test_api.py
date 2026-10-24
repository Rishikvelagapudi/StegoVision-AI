"""HTTP-level tests. Require fastapi + httpx (see requirements.txt); skipped if unavailable."""
import io
import json

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("multipart")

from fastapi.testclient import TestClient  # noqa: E402

from app.core import stego_format as sf  # noqa: E402
from app.main import create_app  # noqa: E402
from tests.helpers import carrier, png_bytes, secret_png  # noqa: E402


def client():
    return TestClient(create_app())


def test_health():
    r = client().get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["ai_model_available"] is False


def test_root_and_favicon():
    c = client()
    r = c.get("/")
    assert r.status_code == 200
    fav = c.get("/favicon.ico")
    assert fav.status_code in (200, 204)


def test_full_http_flow_with_byte_equal_recovery():
    c = client()
    secret = secret_png()
    st = sf.encode_to_png_bytes(carrier(), secret, sf.TYPE_PNG)
    r = c.post("/api/analyze", files={"file": ("stego.png", st, "image/png")})
    assert r.status_code == 201
    aid = r.json()["analysis_id"]
    assert r.json()["detection"]["outcome"] == "Possible Steganography Detected"
    assert c.get(f"/api/analysis/{aid}").status_code == 200
    assert c.get(f"/api/analysis/{aid}/recovered").status_code == 404  # before extraction
    e = c.post(f"/api/extract/{aid}")
    assert e.status_code == 200 and e.json()["extraction"]["status"] == "success"
    rec = c.get(f"/api/analysis/{aid}/recovered")
    assert rec.status_code == 200 and rec.content == secret
    assert rec.headers["x-content-type-options"] == "nosniff"
    pdf = c.get(f"/api/analysis/{aid}/report")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    js = c.get(f"/api/analysis/{aid}/json")
    assert js.status_code == 200 and json.loads(js.content)["analysis_id"] == aid
    assert c.get(f"/api/analysis/{aid}/original").content == st
    assert c.get(f"/api/analysis/{aid}/lsb-visualization").headers["content-type"] == "image/png"


def test_error_responses_are_structured():
    c = client()
    r = c.post("/api/analyze", files={"file": ("x.png", b"nope", "image/png")})
    assert r.status_code == 415 and r.json()["error"]["code"] == "unsupported_format"
    r = c.post("/api/analyze", files={"file": ("x.png", png_bytes(carrier(size=64))[:90], "image/png")})
    assert r.status_code == 422 and r.json()["error"]["code"] == "corrupted_image"
    assert c.post("/api/analyze").status_code == 422
    assert c.get("/api/analysis/" + "0" * 32).status_code == 404
    assert c.get("/api/analysis/..%2f..%2fetc%2fpasswd").status_code == 404
    assert c.post("/api/extract/" + "a" * 32).status_code == 404


def test_stego_encode_endpoint_demo_and_custom():
    c = client()
    r = c.post("/api/stego/encode", data={"secret_text": "hi there"})
    assert r.status_code == 200 and r.headers["x-stego-payload-type"] == "text"
    a = c.post("/api/analyze", files={"file": ("g.png", r.content, "image/png")}).json()
    assert c.post(f"/api/extract/{a['analysis_id']}").json()["extraction"]["recovered"]["text_preview"] == "hi there"
    r = c.post("/api/stego/encode", files={"carrier": ("c.png", png_bytes(carrier()), "image/png"),
                                           "secret_image": ("s.png", secret_png(), "image/png")})
    assert r.status_code == 200 and r.headers["x-stego-payload-type"] == "png"
    r = c.post("/api/stego/encode", files={"secret_image": ("s.png", b"junk", "image/png")})
    assert r.status_code == 415


def test_cors_only_for_configured_origin():
    c = client()
    ok = c.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = c.get("/api/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in bad.headers
