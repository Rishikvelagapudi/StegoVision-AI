import numpy as np
from PIL import Image

from app import service
from app.core import detection as d
from app.core import stego_format as sf
from tests.helpers import carrier, jpeg_bytes, png_bytes, random_lsb_overwrite, secret_png


def _outcome(blob):
    return service.analyze("t.png", blob)["detection"]["outcome"]


def test_clean_images_are_never_flagged_possible():
    for seed in (1, 2, 3, 4, 5):
        out = _outcome(png_bytes(carrier(seed=seed, size=384)))
        assert out in (d.OUTCOME_NONE, d.OUTCOME_INCONCLUSIVE), (seed, out)


def test_clean_image_reports_no_strong_evidence_on_typical_case():
    assert _outcome(png_bytes(carrier(seed=2, size=384))) == d.OUTCOME_NONE


def test_known_custom_stego_flagged():
    st = sf.encode_to_png_bytes(carrier(), secret_png(), sf.TYPE_PNG)
    rec = service.analyze("s.png", st)
    assert rec["detection"]["outcome"] == d.OUTCOME_POSSIBLE
    sig = [x for x in rec["detection"]["detectors"] if x["name"] == "custom_signature"][0]
    assert sig["signal"] == d.STRONG_FOR and sig["kind"] == "measured"


def test_signatureless_dense_lsb_noise_flagged_by_statistics():
    img = random_lsb_overwrite(carrier(size=384), 0.6)
    rec = service.analyze("n.png", png_bytes(img))
    assert rec["detection"]["outcome"] == d.OUTCOME_POSSIBLE
    rs = [x for x in rec["detection"]["detectors"] if x["name"] == "rs_analysis"][0]
    assert rs["details"]["estimated_payload_fraction"] > 0.3


def test_jpeg_is_inconclusive_not_clean():
    rec = service.analyze("j.jpg", jpeg_bytes(carrier(size=256)))
    assert rec["detection"]["outcome"] == d.OUTCOME_INCONCLUSIVE


def test_ai_unavailable_without_model_and_no_confidence_invented():
    rec = service.analyze("c.png", png_bytes(carrier()))
    ai = rec["detection"]["ai"]
    assert ai["available"] is False and ai["prediction"] is None and ai["confidence"] is None


def test_appended_png_flagged():
    blob = png_bytes(carrier()) + secret_png()
    rec = service.analyze("a.png", blob)
    assert rec["detection"]["outcome"] == d.OUTCOME_POSSIBLE
    assert rec["metadata"]["measured"]["trailing_data_type"] == "PNG image"


def test_metadata_alone_does_not_prove_steganography():
    blob = png_bytes(carrier()) + b"\x00" * 64  # unidentified trailing bytes: weak indicator only
    rec = service.analyze("m.png", blob)
    assert rec["detection"]["outcome"] != d.OUTCOME_POSSIBLE


def test_pipeline_is_extensible():
    before = len(d.DETECTORS)

    @d.register_detector("unit_test_detector")
    def _fn(ctx):
        return {"name": "unit_test_detector", "kind": "heuristic", "signal": d.NEUTRAL, "summary": "x", "details": {}}

    try:
        rec = service.analyze("e.png", png_bytes(carrier()))
        assert "unit_test_detector" in [x["name"] for x in rec["detection"]["detectors"]]
    finally:
        d.DETECTORS.pop()
    assert len(d.DETECTORS) == before
