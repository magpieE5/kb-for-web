import typer
import duckdb
import re
import yaml
from typing import Annotated
from pathlib import Path
from commands import PARQUET_PATH, KB_DIR

IMPORT_HELP = "Rebuild parquet from markdown files."


def _rebuild_parquet(input_dir=KB_DIR, quiet=False):
    """Rebuild parquet from markdown. Always clears and rebuilds."""
    if not input_dir.exists():
        if not quiet:
            print(f"not found: {input_dir}")
        return 0

    con = duckdb.connect()
    con.execute("""
        CREATE TABLE knowledge (
            id VARCHAR PRIMARY KEY, category VARCHAR, title VARCHAR,
            content TEXT, updated TIMESTAMP
        )
    """)

    count = 0
    for md_file in input_dir.rglob("*.md"):
        try:
            text = md_file.read_text(encoding='utf-8')
            if not text.startswith('---'):
                continue
            parts = text.split('---', 2)
            if len(parts) < 3:
                continue

            fm = yaml.safe_load(parts[1])
            body = parts[2].strip()

            # Clean auto-generated title/footer
            body = re.sub(r'^#\s+.*?\n+', '', body, count=1)
            while re.search(r'\n+---\s*\n+\*KB Entry:.*?\*', body, flags=re.DOTALL):
                body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*', '', body, flags=re.DOTALL)
            body = re.sub(r'\n+---\s*$', '', body)

            missing = [f for f in ('id', 'category', 'title', 'updated') if f not in fm]
            if missing:
                if not quiet:
                    print(f"  skip {md_file.name}: missing {', '.join(missing)}")
                continue

            con.execute(
                "INSERT INTO knowledge VALUES (?, ?, ?, ?, ?)",
                [fm['id'], fm['category'], fm['title'], body.strip(), fm['updated']],
            )
            count += 1
        except Exception:
            continue

    con.execute(f"COPY knowledge TO '{PARQUET_PATH}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.close()

    if not quiet:
        print(f"imported={count}")
    return count


def import_kb(
    input_dir: Annotated[Path, typer.Argument(help="Markdown directory")] = KB_DIR,
):
    _rebuild_parquet(input_dir)
