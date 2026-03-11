"""Final open step — prints selected entry IDs, history entry IDs, and todos."""
import typer
from typing import List, Optional
from commands import KB_DIR, connect

OPEN_SELECT_HELP = "Print selected entry IDs, history entry IDs, and show todos."


def open_select(
    selections: Optional[List[str]] = typer.Argument(default=None, help="Entry IDs, 'all', or 'none'"),
):
    con = connect()

    mode_marker = KB_DIR / ".open_modes_selected"
    if not mode_marker.exists() or not mode_marker.read_text().strip():
        manual_entries = []
    else:
        resolved = mode_marker.read_text().strip().split("\n")
        placeholders = ",".join(f"'{m}'" for m in resolved)
        seed_ids = set(r[0] for r in con.execute("SELECT id FROM kb_mode WHERE mode = 'seed'").fetchall())

        rows = con.execute(f"""
            SELECT DISTINCT m.id
            FROM kb_mode m
            JOIN kb_knowledge k ON m.id = k.id
            WHERE m.mode IN ({placeholders})
              AND m.is_auto = false
              AND m.id NOT IN (SELECT id FROM kb_mode WHERE is_auto = true AND mode IN ({placeholders}))
        """).fetchall()
        manual_entries = sorted([r[0] for r in rows if r[0] not in seed_ids])

    selections_str = " ".join(selections).strip().lower() if selections else "none"
    selected = []
    if selections_str in ("none", ""):
        pass
    elif selections_str == "all":
        selected = manual_entries
    else:
        for token in selections_str.replace(",", " ").split():
            token = token.strip()
            if token in manual_entries:
                selected.append(token)
            elif token:
                print(f"warning: unknown entry '{token}'")

    if selected:
        print("load:")
        for entry_id in selected:
            print(f"  {entry_id}")
    else:
        print("load: none")

    # History
    resolved = (
        mode_marker.read_text().strip().split("\n")
        if mode_marker.exists() and mode_marker.read_text().strip()
        else []
    )
    history_ids = []

    for mode in resolved:
        depth_row = con.execute(
            "SELECT transcript_depth, log_depth FROM kb_mode_config WHERE mode = ?", [mode]
        ).fetchone()
        if not depth_row:
            continue
        transcript_depth, log_depth = depth_row

        if log_depth and log_depth > 0:
            logs = con.execute(f"""
                SELECT id FROM kb_knowledge WHERE category = 'log'
                ORDER BY updated DESC LIMIT {log_depth}
            """).fetchall()
            for (log_id,) in reversed(logs):
                if log_id not in history_ids:
                    history_ids.append(log_id)

        if transcript_depth and transcript_depth > 0:
            transcripts = con.execute(f"""
                SELECT id FROM kb_knowledge WHERE category = 'transcript'
                ORDER BY updated DESC LIMIT {transcript_depth}
            """).fetchall()
            for (t_id,) in reversed(transcripts):
                if t_id not in history_ids:
                    history_ids.append(t_id)

    if history_ids:
        print()
        print("history:")
        for entry_id in history_ids:
            print(f"  {entry_id}")

    total = con.execute(
        "SELECT COUNT(*) FROM kb_knowledge WHERE category NOT IN ('log', 'transcript')"
    ).fetchone()[0]
    print(f"kb_entries: {total}")

    todos = con.execute("""
        SELECT todo, type, narrative, mode, updated
        FROM kb_todo WHERE is_active = 'Y'
        ORDER BY type, updated DESC
    """).fetchall()

    if todos:
        print()
        print("Active todos:")
        for todo, ttype, narrative, mode, updated in todos:
            parts = [f"  {todo} ({ttype})"]
            if narrative and str(narrative) != 'None':
                parts.append(f"- {narrative}")
            if mode and str(mode) != 'None':
                parts.append(f"[{mode}]")
            parts.append(f"[{updated}]")
            print(" ".join(parts))

    con.close()
