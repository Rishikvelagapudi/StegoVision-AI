// Thin client for the StegoVision FastAPI backend. Every call hits a real endpoint.
export const API_BASE = (import.meta.env?.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, code = "error", status = 0) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

const url = (path) => `${API_BASE}${path}`;

async function parseError(res) {
  try {
    const body = await res.json();
    if (body?.error) return new ApiError(body.error.message, body.error.code, res.status);
  } catch (_) { /* not JSON */ }
  return new ApiError(`Request failed (${res.status}).`, "http_error", res.status);
}

async function request(path, options) {
  let res;
  try {
    res = await fetch(url(path), options);
  } catch (_) {
    throw new ApiError("Cannot reach the StegoVision backend. Is it running and is VITE_API_BASE_URL / CORS configured?", "network_error");
  }
  if (!res.ok) throw await parseError(res);
  return res;
}

export const health = async () => (await request("/api/health")).json();
export const getAnalysis = async (id) => (await request(`/api/analysis/${id}`)).json();
export const extract = async (id) => (await request(`/api/extract/${id}`, { method: "POST" })).json();

/** Upload with real progress events (fetch cannot report upload progress). */
export function analyze(file, onUploadProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const form = new FormData();
    form.append("file", file, file.name);
    xhr.open("POST", url("/api/analyze"));
    xhr.upload.onprogress = (e) => e.lengthComputable && onUploadProgress?.(e.loaded / e.total);
    xhr.onerror = () => reject(new ApiError("Cannot reach the StegoVision backend. Is it running and is VITE_API_BASE_URL / CORS configured?", "network_error"));
    xhr.onload = () => {
      let body = null;
      try { body = JSON.parse(xhr.responseText); } catch (_) { /* ignore */ }
      if (xhr.status >= 200 && xhr.status < 300 && body) return resolve(body);
      reject(new ApiError(body?.error?.message || `Analysis failed (${xhr.status}).`, body?.error?.code || "http_error", xhr.status));
    };
    xhr.send(form);
  });
}

export async function fetchBlob(path) {
  const res = await request(path);
  return res.blob();
}

export const endpoints = {
  original: (id) => `/api/analysis/${id}/original`,
  lsb: (id) => `/api/analysis/${id}/lsb-visualization`,
  recovered: (id) => `/api/analysis/${id}/recovered`,
  report: (id) => `/api/analysis/${id}/report`,
  json: (id) => `/api/analysis/${id}/json`,
};

/** Download a backend file through fetch so errors surface in the UI. */
export async function download(path, filename) {
  const blob = await fetchBlob(path);
  const href = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(href), 10_000);
}

export function saveBlob(blob, filename) {
  const href = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(href), 10_000);
}

/** Create a TEST stego image (StegoVision custom format). All inputs optional -> demo mode. */
export async function encodeStego({ carrier, secretImage, secretText }) {
  const form = new FormData();
  if (carrier) form.append("carrier", carrier, carrier.name);
  if (secretImage) form.append("secret_image", secretImage, secretImage.name);
  if (secretText) form.append("secret_text", secretText);
  const res = await request("/api/stego/encode", { method: "POST", body: form });
  const h = res.headers;
  return {
    blob: await res.blob(),
    info: {
      payloadType: h.get("X-Stego-Payload-Type"),
      payloadBytes: Number(h.get("X-Stego-Payload-Bytes")),
      capacityBytes: Number(h.get("X-Stego-Capacity-Bytes")),
      demoCarrier: h.get("X-Stego-Demo-Carrier") === "true",
      demoPayload: h.get("X-Stego-Demo-Payload") === "true",
    },
  };
}
