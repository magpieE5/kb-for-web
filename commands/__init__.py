from pathlib import Path
import duckdb

ROOT = Path(__file__).parent.parent
KB_DIR = ROOT / "kb"
PARQUET_PATH = KB_DIR / "kb.parquet"


def connect():
    """In-memory DuckDB with KB views. Rebuilt each invocation — fast at KB scale."""
    con = duckdb.connect()
    if PARQUET_PATH.exists():
        con.execute(f"CREATE VIEW kb_knowledge AS SELECT * FROM read_parquet('{PARQUET_PATH}')")
    for csv_name, view_name in [
        ("kb-mode.csv", "kb_mode"),
        ("kb-mode-config.csv", "kb_mode_config"),
        ("kb-todo.csv", "kb_todo"),
        ("kb-query-log.csv", "kb_query_log"),
    ]:
        path = KB_DIR / csv_name
        if path.exists():
            con.execute(
                f"CREATE VIEW {view_name} AS SELECT * FROM read_csv('{path}', header=true, null_padding=true)"
            )
    return con
