import typer
from commands import connect

LIST_KB_HELP = "List KB entries (excludes logs and transcripts)."


def list_kb():
    con = connect()
    rows = con.execute(
        "SELECT id, title FROM kb_knowledge WHERE category NOT IN ('log', 'transcript') ORDER BY category, id"
    ).fetchall()
    con.close()
    for row in rows:
        print(f"{row[0]}\t{row[1]}")
