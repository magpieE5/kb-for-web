import csv
import typer
from datetime import datetime
from typing import Annotated
from commands import KB_DIR, connect

QUERY_HELP = "Run SQL against KB views (kb_knowledge, kb_mode, kb_mode_config, kb_todo, kb_query_log)."

QUERY_LOG = KB_DIR / "kb-query-log.csv"


def _log_query(sql: str):
    session = ""
    session_file = KB_DIR / ".session"
    if session_file.exists():
        lines = session_file.read_text().strip().splitlines()
        if lines:
            session = lines[0]
    write_header = not QUERY_LOG.exists()
    with open(QUERY_LOG, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["ts", "session", "sql"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), session, sql])


def query(sql: Annotated[str, typer.Argument(help="SQL query")]):
    _log_query(sql)
    con = connect()
    con.execute(sql)
    rows = con.fetchall()
    cols = [desc[0] for desc in con.description]
    con.close()
    print("\t".join(cols))
    for row in rows:
        print("\t".join(str(v) for v in row))
