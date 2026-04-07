"""
Entrada WSGI para Gunicorn en producción (Render, Railway, etc.).

  gunicorn wsgi:app

El bloque if __name__ == "__main__" de app.py no se ejecuta con Gunicorn;
aquí se hace create_all, usuarios por defecto y migraciones ligeras al arrancar.
"""
from __future__ import annotations

import os
import sys


def _abort_startup(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


if not (os.environ.get("DATABASE_URL") or "").strip():
    _abort_startup(
        "Render: falta DATABASE_URL. Ve a tu Web Service → Environment → añade "
        "DATABASE_URL (igual que en tu .env local, pooler Supabase)."
    )

_debug = os.environ.get("FLASK_DEBUG", "1") == "1"
_sk = os.environ.get("SECRET_KEY") or ""
if not _debug and (
    not _sk.strip() or _sk == "dev-only-cambiar-en-produccion"
):
    _abort_startup(
        "Render: con FLASK_DEBUG=0 debes definir SECRET_KEY (cadena larga y aleatoria) "
        "en Environment."
    )

from werkzeug.middleware.proxy_fix import ProxyFix

from app import app as flask_app
from app import crear_usuarios_default, db, ensure_columns, sync_postgres_sequences


def _bootstrap() -> None:
    if os.environ.get("SKIP_APP_BOOTSTRAP") == "1":
        return
    with flask_app.app_context():
        db.create_all()
        crear_usuarios_default()
        ensure_columns()
        sync_postgres_sequences()


_bootstrap()

# Detrás de proxy HTTPS (Render, Railway, nginx)
flask_app.wsgi_app = ProxyFix(
    flask_app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1,
    x_prefix=1,
)

app = flask_app
