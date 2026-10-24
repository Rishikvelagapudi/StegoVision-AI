"""HTTP layer. All logic lives in app.service; this module only adapts it to FastAPI."""
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import Response

from . import __version__, service
from .config import get_settings
from .core import ml

router = APIRouter(prefix="/api")

_SAFE = {"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"}


def _read_upload(upload, limit: int) -> bytes:
    """Read at most limit+1 bytes so oversized uploads are rejected without buffering them fully."""
    if upload is None:
        return None
    return upload.file.read(limit + 1)


def _file_response(blob: bytes, mime: str, filename: str, inline: bool = False) -> Response:
    disp = "inline" if inline else "attachment"
    headers = dict(_SAFE, **{"Content-Disposition": f'{disp}; filename="{filename}"'})
    return Response(content=blob, media_type=mime, headers=headers)


@router.get("/health")
def health():
    s = get_settings()
    return {
        "status": "ok", "version": __version__,
        "ai_model_available": ml.is_available(s.model_path),
        "limits": {"max_upload_bytes": s.max_upload_bytes, "max_dimension": s.max_dimension,
                   "max_pixels": s.max_pixels, "result_ttl_seconds": s.ttl_seconds},
        "supported_formats": ["PNG", "JPEG", "BMP"],
    }


@router.post("/analyze", status_code=201)
def analyze(file: UploadFile = File(...)):
    data = _read_upload(file, get_settings().max_upload_bytes)
    return service.analyze(file.filename, data)


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    return service.get_analysis(analysis_id)


@router.post("/extract/{analysis_id}")
def extract(analysis_id: str):
    return service.extract(analysis_id)


@router.get("/analysis/{analysis_id}/report")
def report_pdf(analysis_id: str):
    blob = service.get_pdf_report(analysis_id)
    return _file_response(blob, "application/pdf", f"stegovision_report_{analysis_id[:8]}.pdf")


@router.get("/analysis/{analysis_id}/json")
def report_json(analysis_id: str):
    blob = service.get_json_report(analysis_id)
    return _file_response(blob, "application/json", f"stegovision_analysis_{analysis_id[:8]}.json")


@router.get("/analysis/{analysis_id}/recovered")
def recovered(analysis_id: str):
    blob, mime, name = service.get_recovered(analysis_id)
    return _file_response(blob, mime, name)


@router.get("/analysis/{analysis_id}/original")
def original(analysis_id: str):
    blob, mime = service.get_original(analysis_id)
    return _file_response(blob, mime, "original_upload", inline=True)


@router.get("/analysis/{analysis_id}/lsb-visualization")
def lsb_visualization(analysis_id: str):
    blob = service.get_lsb_visualization(analysis_id)
    return _file_response(blob, "image/png", "lsb_plane.png", inline=True)


@router.post("/stego/encode")
def stego_encode(carrier: UploadFile = File(None), secret_image: UploadFile = File(None),
                 secret_text: str = Form(None)):
    """Create a TEST stego image in the StegoVision custom format. With no inputs, demo mode
    uses a generated carrier and a generated secret image."""
    s = get_settings()
    out, info = service.encode_test_image(_read_upload(carrier, s.max_upload_bytes),
                                          _read_upload(secret_image, s.max_payload_bytes), secret_text)
    headers = {"X-Stego-Payload-Type": info["payload_type"], "X-Stego-Payload-Bytes": str(info["payload_bytes"]),
               "X-Stego-Capacity-Bytes": str(info["capacity_bytes"]),
               "X-Stego-Demo-Carrier": str(info["demo_carrier"]).lower(),
               "X-Stego-Demo-Payload": str(info["demo_payload"]).lower()}
    resp = _file_response(out, "image/png", "stego_test_image.png")
    resp.headers.update(headers)
    return resp
