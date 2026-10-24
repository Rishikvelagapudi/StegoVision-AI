import io
import json

from PIL import Image

from app import service
from app.core import stego_format as sf
from tests.helpers import carrier, png_bytes, secret_png


def test_json_report_contains_required_fields():
    rec = service.analyze("clean.png", png_bytes(carrier()))
    doc = json.loads(service.get_json_report(rec["analysis_id"]))
    for key in ("analysis_id", "timestamp", "filename", "sha256", "image", "metadata", "statistics", "lsb",
                "detection", "extraction", "limitations"):
        assert key in doc, key
    assert doc["image"]["width"] == 256 and doc["detection"]["ai"]["available"] is False
    assert doc["extraction"]["status"] == "not_attempted"


def test_pdf_report_clean_and_with_recovered_image():
    clean = service.analyze("clean.png", png_bytes(carrier()))
    pdf = service.get_pdf_report(clean["analysis_id"])
    assert pdf.startswith(b"%PDF") and len(pdf) > 2000

    st = sf.encode_to_png_bytes(carrier(), secret_png(), sf.TYPE_PNG)
    rec = service.analyze("stego.png", st)
    before = len(service.get_pdf_report(rec["analysis_id"]))
    service.extract(rec["analysis_id"])
    after_pdf = service.get_pdf_report(rec["analysis_id"])
    assert after_pdf.startswith(b"%PDF") and len(after_pdf) > before  # thumbnail + extraction section added
    doc = json.loads(service.get_json_report(rec["analysis_id"]))
    assert doc["extraction"]["recovered"]["sha256"]


def test_pdf_handles_hostile_text_in_filename_and_text_payload():
    st = sf.encode_to_png_bytes(carrier(), b"<b>bold</b> & <script>alert(1)</script> \xe2\x9c\x93", sf.TYPE_TEXT)
    rec = service.analyze("<i>evil</i>&.png", st)
    service.extract(rec["analysis_id"])
    assert service.get_pdf_report(rec["analysis_id"]).startswith(b"%PDF")


def test_lsb_visualization_is_png_and_labeled_separately():
    rec = service.analyze("c.png", png_bytes(carrier()))
    viz = service.get_lsb_visualization(rec["analysis_id"])
    img = Image.open(io.BytesIO(viz))
    assert img.format == "PNG"
    assert "recovered" not in rec["extraction"] or rec["extraction"]["recovered"] is None
