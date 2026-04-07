"""Ensambla DATABASE_URL + DATABASE_PASSWORD sin ambigüedades de @ en la clave."""
from __future__ import annotations

import os

from sqlalchemy.engine.url import URL, make_url


def _strip_psycopg2_incompatible_query(u: URL) -> URL:
    """libpq/psycopg2 reject some Supabase URI params (e.g. pgbouncer=true)."""
    if not u.query or "pgbouncer" not in u.query:
        return u
    return u.difference_update_query(["pgbouncer"])


def resolve_database_uri() -> str:
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        raise RuntimeError(
            "Falta DATABASE_URL (archivo .env local o variables en Render / hosting)."
        )
    low = raw.lower()
    if low.startswith("https://") or low.startswith("http://"):
        raise RuntimeError(
            "DATABASE_URL no puede ser una URL https del navegador (p. ej. https://xxx.supabase.co). "
            "Usa la cadena de conexión PostgreSQL: Supabase → Project Settings → Database → "
            "Connection string → URI; debe empezar por postgresql:// o postgres:// "
            "(Transaction pooler :6543 recomendado)."
        )
    u = _strip_psycopg2_incompatible_query(make_url(raw))
    pw = os.environ.get("DATABASE_PASSWORD")
    if pw is not None and str(pw).strip() != "":
        u = u.set(password=str(pw))
    return u.render_as_string(hide_password=False)
