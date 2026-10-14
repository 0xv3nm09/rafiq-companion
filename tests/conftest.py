import os
import tempfile

# Isolate the file-backed runtime (consent/audit/handoffs/notices) per test session.
os.environ.setdefault("RUNTIME_DIR", tempfile.mkdtemp(prefix="rafiq-test-runtime-"))

import pytest  # noqa: E402

from app.services.data import load_store  # noqa: E402

_RUNTIME_FILES = ("notices.json", "handoffs.json", "audit.json", "consent.json", "requests_created.json")


@pytest.fixture(autouse=True)
def clean_runtime():
    from app.config import get_settings
    rd = get_settings().runtime_dir
    rd.mkdir(parents=True, exist_ok=True)
    for f in _RUNTIME_FILES:
        p = rd / f
        if p.exists():
            p.unlink()
    yield


@pytest.fixture(scope="session")
def store():
    return load_store()
