"""Ensambla DATABASE_URL + DATABASE_PASSWORD sin ambigüedades de @ en la clave."""
from __future__ import annotations

import os

from sqlalchemy.engine.url import make_url


def resolve_database_uri() -> str:
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        raise RuntimeError(
            "Falta DATABASE_URL (archivo .env local o variables en Render / hosting)."
        )
    pw = os.environ.get("DATABASE_PASSWORD")
    if pw is not None and str(pw).strip() != "":
        u = make_url(raw)
        u = u.set(password=str(pw))
        return u.render_as_string(hide_password=False)
    return raw
