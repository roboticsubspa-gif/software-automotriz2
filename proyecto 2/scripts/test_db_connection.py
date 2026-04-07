"""Prueba DATABASE_URL sin escribir la contraseña en la línea de comandos."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(override=True)

from db_uri import resolve_database_uri


def main() -> int:
    try:
        url = resolve_database_uri()
    except RuntimeError as e:
        print(e)
        return 1
    from sqlalchemy import create_engine, text

    connect_args = {}
    if "supabase.co" in url or "pooler.supabase.com" in url:
        connect_args["sslmode"] = "require"
    if ":6543" in url:
        connect_args["prepare_threshold"] = None

    try:
        eng = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
        with eng.connect() as c:
            c.execute(text("SELECT 1"))
        print("OK: conexión correcta")
        return 0
    except Exception as e:
        print("Error:", type(e).__name__, e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
