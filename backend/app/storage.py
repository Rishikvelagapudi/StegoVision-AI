"""Ephemeral, thread-safe result store.

Records live in memory; binary artefacts are written to a private temp directory under
server-generated names (<analysis_id>/<kind>.bin, kind from a fixed whitelist). Nothing is
persisted beyond RESULT_TTL_SECONDS or process exit, and no client-supplied string is ever
used to build a path. On cloud hosts with ephemeral disks this behaves identically.
"""
import atexit
import os
import re
import shutil
import tempfile
import threading
import time
import uuid

from .errors import NotFoundError

ID_RE = re.compile(r"^[0-9a-f]{32}$")
KINDS = ("original", "recovered", "lsb")


class Store:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._lock = threading.RLock()
        self._records = {}
        self._dir = tempfile.mkdtemp(prefix="stegovision_")
        os.chmod(self._dir, 0o700)
        atexit.register(self.purge_all)

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex

    def _check(self, analysis_id: str):
        if not isinstance(analysis_id, str) or not ID_RE.match(analysis_id):
            raise NotFoundError()

    def _path(self, analysis_id: str, kind: str) -> str:
        if kind not in KINDS:
            raise ValueError("invalid artefact kind")
        return os.path.join(self._dir, analysis_id, kind + ".bin")

    def put(self, analysis_id: str, record: dict, files: dict):
        with self._lock:
            os.makedirs(os.path.join(self._dir, analysis_id), mode=0o700, exist_ok=True)
            for kind, blob in files.items():
                self.write_file(analysis_id, kind, blob)
            self._records[analysis_id] = {"record": record, "created": time.time()}
        self.cleanup_expired()

    def write_file(self, analysis_id: str, kind: str, blob: bytes):
        path = self._path(analysis_id, kind)
        tmp = path + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(blob)
        os.replace(tmp, path)

    def delete_file(self, analysis_id: str, kind: str):
        try:
            os.remove(self._path(analysis_id, kind))
        except FileNotFoundError:
            pass

    def get(self, analysis_id: str) -> dict:
        self._check(analysis_id)
        with self._lock:
            item = self._records.get(analysis_id)
            if not item or time.time() - item["created"] > self.ttl:
                self._drop(analysis_id)
                raise NotFoundError()
            return item["record"]

    def update(self, analysis_id: str, **fields):
        with self._lock:
            rec = self.get(analysis_id)
            rec.update(fields)
            return rec

    def read_file(self, analysis_id: str, kind: str):
        self._check(analysis_id)
        with self._lock:
            self.get(analysis_id)
            try:
                with open(self._path(analysis_id, kind), "rb") as fh:
                    return fh.read()
            except FileNotFoundError:
                return None

    def _drop(self, analysis_id: str):
        self._records.pop(analysis_id, None)
        shutil.rmtree(os.path.join(self._dir, analysis_id), ignore_errors=True)

    def cleanup_expired(self):
        now = time.time()
        with self._lock:
            for aid in [a for a, i in self._records.items() if now - i["created"] > self.ttl]:
                self._drop(aid)

    def purge_all(self):
        with self._lock:
            self._records.clear()
        shutil.rmtree(self._dir, ignore_errors=True)
