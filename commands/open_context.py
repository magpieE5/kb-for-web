"""Core context loading — prints seed entry IDs and available modes."""
import typer
from commands import KB_DIR, connect
from commands.session_details import get_session_details
from commands.import_md import import_kb as _import_kb

OPEN_CONTEXT_HELP = "Import KB, set session, print seed entry IDs and available modes."


def open_context():
    details = get_session_details()
    session_number = details['session_number']

    print(f"session: {session_number}")
    print(f"date: {details['date_display']}")
    print(f"client: {details['client']}")

    _import_kb(KB_DIR)

    marker = KB_DIR / ".session"
    marker.write_text(f"{session_number}\n{details['client']}\n")
    print(f"session_set: {session_number}")

    con = connect()

    seed_rows = con.execute("""
        SELECT id FROM kb_mode
        WHERE mode = 'seed'
        ORDER BY load_order
    """).fetchall()

    print()
    print("load:")
    for (entry_id,) in seed_rows:
        print(f"  {entry_id}")

    modes = con.execute("""
        SELECT DISTINCT m.mode
        FROM kb_mode m
        LEFT JOIN kb_mode_config c USING (mode)
        WHERE m.mode <> 'seed'
        ORDER BY c.display_order, m.mode
    """).fetchall()
    mode_list = [r[0] for r in modes]

    print()
    print("Available modes:")
    half = (len(mode_list) + 1) // 2
    for i in range(half):
        left = f"  {mode_list[i]}"
        right = f"  {mode_list[i+half]}" if i + half < len(mode_list) else ""
        print(f"{left:<25s}{right}")

    con.close()
