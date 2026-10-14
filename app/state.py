"""Process-wide singletons (store, index). Tests build their own stores."""
from __future__ import annotations

from functools import lru_cache

from app.services.data import DataStore, load_store


@lru_cache
def get_store() -> DataStore:
    return load_store()
