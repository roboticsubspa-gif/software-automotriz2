"""
Importa backup_supabase.sql usando .env (DATABASE_URL + DATABASE_PASSWORD).

1) Si existe psql -> lo usa.
2) Si no -> importa con psycopg2 (DDL por sentencias; sin psql en PATH).

Uso (raiz del proyecto):
  .\\.venv\\Scripts\\python scripts\\import_to_supabase.py
"""
from __future__ import annotations

import io
import os
import re
import subprocess
import sys
from shutil import which

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

load_dotenv(override=True)

from db_uri import resolve_database_uri

COPY_LINE = re.compile(r"^COPY public\.(\w+) \(([^)]+)\) FROM stdin;\s*$")

# pg_dump ordena COPY alfabeticamente; ot/servicio quedan antes que vehiculo (FK).
_COPY_ORDER = (
    "cliente",
    "usuario",
    "repuesto",
    "cotizacion",
    "gasto_st",
    "tarea",
    "toma_hora",
    "vehiculo",
    "ot",
    "servicio",
    "repuesto_usado",
)


def _parse_dump_copies(sql_path: str) -> tuple[str, dict[str, tuple[str, str]]]:
    """Devuelve (texto DDL sin bloques COPY, {tabla: (columnas, datos)})."""
    ddl_lines: list[str] = []
    copies: dict[str, tuple[str, str]] = {}
    with open(sql_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = COPY_LINE.match(line)
            if m:
                table = m.group(1)
                cols = m.group(2)
                parts: list[str] = []
                for cline in f:
                    if cline.rstrip("\r\n") == "\\.":
                        break
                    parts.append(cline)
                copies[table] = (cols, "".join(parts))
            else:
                ddl_lines.append(line)
    return "".join(ddl_lines), copies


def _find_psql_exe() -> str | None:
    override = (os.environ.get("PSQL_EXE") or "").strip().strip('"')
    if override and os.path.isfile(override):
        return override
    for name in ("psql", "psql.exe"):
        p = which(name)
        if p and os.path.isfile(p):
            return p
    if sys.platform != "win32":
        return None
    for env in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(env)
        if not base:
            continue
        pg_root = os.path.join(base, "PostgreSQL")
        if not os.path.isdir(pg_root):
            continue
        try:
            versions = sorted(os.listdir(pg_root), reverse=True)
        except OSError:
            continue
        for ver in versions:
            candidate = os.path.join(pg_root, ver, "bin", "psql.exe")
            if os.path.isfile(candidate):
                return candidate
    return None


def _connect_psycopg(u):
    import psycopg2

    kwargs = dict(
        host=u.host,
        port=u.port or 5432,
        user=u.username,
        password=u.password or "",
        dbname=u.database or "postgres",
        sslmode="require",
        connect_timeout=90,
    )
    if (u.port or 5432) == 6543:
        kwargs["options"] = "-c statement_timeout=600000"
    conn = psycopg2.connect(**kwargs)
    conn.autocommit = True
    return conn


def _ddl_comment_only(stmt: str) -> bool:
    for ln in stmt.splitlines():
        s = ln.strip()
        if not s:
            continue
        if not s.startswith("--"):
            return False
    return True


def _run_ddl(cur, buf_lines: list[str]) -> None:
    import time

    text = "".join(buf_lines).strip()
    if not text:
        return
    text = text.replace("\r\n", "\n")
    kb = max(1, len(text) // 1024)
    print(f"  Aplicando DDL (~{kb} KB, sentencias separadas por ';' al final de línea)...", flush=True)
    t0 = time.time()
    parts = re.split(r";\s*\n", text)
    n_ok = 0
    for part in parts:
        stmt = part.strip()
        if not stmt or _ddl_comment_only(stmt):
            continue
        stmt = stmt + ";"
        try:
            cur.execute(stmt)
            n_ok += 1
            if n_ok % 30 == 0:
                print(f"  ... {n_ok} sentencias DDL", flush=True)
        except Exception as e:
            err = str(e).lower()
            if any(
                x in err
                for x in (
                    "must be owner",
                    "permission denied",
                    "only superuser",
                    "unsupported on a logical replication slot",
                )
            ):
                print("  (omitido DDL):", stmt[:70].replace("\n", " "), "...", flush=True)
                continue
            print("Error en SQL:", stmt[:200], "...", flush=True)
            raise
    print(f"  DDL listo: {n_ok} sentencias en {time.time() - t0:.1f}s.", flush=True)


def _import_with_psycopg2(sql_path: str, u) -> None:
    print("psql no encontrado: importando con Python (psycopg2)...", flush=True)
    print("  Leyendo backup y extrayendo bloques COPY...", flush=True)
    ddl_text, copies_map = _parse_dump_copies(sql_path)
    print(f"  {len(copies_map)} tablas con datos; conectando...", flush=True)
    conn = _connect_psycopg(u)
    print("  Conexión OK.", flush=True)
    cur = conn.cursor()
    _run_ddl(cur, ddl_text.splitlines(keepends=True))
    n = 0
    ordered = [t for t in _COPY_ORDER if t in copies_map]
    extra = sorted(set(copies_map) - set(ordered))
    for table in ordered + extra:
        cols, data = copies_map[table]
        rows = data.count("\n") if data else 0
        if data and not data.endswith("\n"):
            rows += 1
        sql = (
            f"COPY public.{table} ({cols}) "
            f"FROM STDIN WITH (FORMAT text, ENCODING 'UTF8')"
        )
        cur.copy_expert(sql, io.StringIO(data))
        n += 1
        print(f"  COPY public.{table} ({rows} filas)", flush=True)
    cur.close()
    conn.close()
    print(f"Listo: {n} bloques COPY + DDL.", flush=True)


def _import_with_psql(psql_exe: str, sql_path: str, u) -> None:
    env = os.environ.copy()
    if u.password:
        env["PGPASSWORD"] = u.password
    env["PGSSLMODE"] = "require"
    port = u.port or 5432
    dbn = u.database or "postgres"
    cmd = [
        psql_exe,
        "-h",
        u.host,
        "-p",
        str(port),
        "-U",
        u.username,
        "-d",
        dbn,
        "-v",
        "ON_ERROR_STOP=1",
        "-f",
        sql_path,
    ]
    print("Ejecutando psql -h", u.host, "-p", port, "-U", u.username, "-d", dbn)
    print(
        "(Si falla FK en ot/vehiculo: este dump ordena COPY alfabeticamente. "
        "Renombra psql.exe temporalmente o quita PATH para forzar import Python.)"
    )
    subprocess.run(cmd, env=env, check=True)


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_path = os.path.join(root, "backup_supabase.sql")
    if not os.path.isfile(sql_path):
        print("No existe backup_supabase.sql en la raiz del proyecto.")
        return 1

    raw = resolve_database_uri()
    u = make_url(raw)
    if not u.host or not u.username:
        print("URL incompleta (host/usuario).")
        return 1

    print("import_to_supabase (v2: psql opcional, import Python si no hay psql)", flush=True)
    print("Archivo:", sql_path, flush=True)
    psql_exe = _find_psql_exe()
    try:
        if psql_exe:
            _import_with_psql(psql_exe, sql_path, u)
        else:
            _import_with_psycopg2(sql_path, u)
    except subprocess.CalledProcessError:
        print(
            "psql fallo. Prueba de nuevo o usa solo Python: desinstala/conflictos psql, "
            "o Session pooler (5432) si COPY falla en 6543."
        )
        return 1
    except Exception as e:
        print("Error:", type(e).__name__, e, flush=True)
        el = str(e).lower()
        if "already exists" in el or "duplicate" in el:
            print(
                "Las tablas u objetos ya existen. Para importar de cero, ejecuta en Supabase "
                "(SQL Editor) el contenido de scripts/drop_app_tables.sql y vuelve a correr este script.",
                flush=True,
            )
        print(
            "Si falla en el pooler :6543, en .env usa Session pooler (5432) temporalmente.",
            flush=True,
        )
        return 1

    print("Importacion terminada. Arranca app.py para sincronizar secuencias.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
