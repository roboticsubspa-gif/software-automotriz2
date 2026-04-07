"""
Quita directivas \\restrict / \\unrestrict de pg_dump 16+ que psql/Supabase pueden rechazar.

Uso:
  python scripts/clean_dump_for_supabase.py "ruta\\backup.sql" "ruta\\backup_supabase.sql"
"""
from __future__ import annotations

import sys


def clean(sql: str) -> str:
    out_lines: list[str] = []
    for line in sql.splitlines():
        s = line.strip()
        if s.startswith("\\restrict ") or s.startswith("\\unrestrict "):
            continue
        out_lines.append(line)
    ends_nl = sql.endswith("\n")
    text = "\n".join(out_lines)
    return text + ("\n" if ends_nl and not text.endswith("\n") else "")


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Uso: python clean_dump_for_supabase.py ENTRADA.sql SALIDA.sql",
            file=sys.stderr,
        )
        return 1
    inp, outp = sys.argv[1], sys.argv[2]
    with open(inp, encoding="utf-8", errors="replace") as f:
        data = f.read()
    cleaned = clean(data)
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        f.write(cleaned)
    print(f"OK: {outp} ({len(cleaned)} caracteres)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
