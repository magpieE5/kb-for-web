"""Mode loading — prints auto-load entry IDs and manual selection list."""
import typer
from typing import List
from commands import KB_DIR, connect

OPEN_MODE_HELP = "Print auto-load entry IDs and manual selection list for chosen modes."


def open_mode(
    modes: List[str] = typer.Argument(help="Mode names (e.g., work personal)"),
):
    modes_str = " ".join(modes).strip().lower()
    if modes_str == "none":
        (KB_DIR / ".open_modes_selected").write_text("")
        print("loaded: none")
        return

    con = connect()

    all_modes = set(
        r[0] for r in con.execute("SELECT DISTINCT mode FROM kb_mode WHERE mode <> 'seed'").fetchall()
    )

    resolved = []
    for token in modes_str.replace(",", " ").split():
        token = token.strip()
        if not token:
            continue
        if token in all_modes:
            resolved.append(token)
        else:
            print(f"warning: unknown mode '{token}'")

    if not resolved:
        print("No valid modes selected.")
        con.close()
        raise typer.Exit(1)

    placeholders = ",".join(f"'{m}'" for m in resolved)
    rows = con.execute(f"""
        SELECT m.mode, m.is_auto, m.id, k.id IS NOT NULL as exists
        FROM kb_mode m
        LEFT JOIN kb_knowledge k ON m.id = k.id
        WHERE m.mode IN ({placeholders})
        ORDER BY m.is_auto DESC, m.id
    """).fetchall()

    for mode, is_auto, entry_id, exists in rows:
        if not exists:
            print(f"warning: {entry_id} not found in KB")

    seen_auto, seen_manual = set(), set()
    auto_entries, manual_entries = [], []
    seed_ids = set(r[0] for r in con.execute("SELECT id FROM kb_mode WHERE mode = 'seed'").fetchall())

    for mode, is_auto, entry_id, exists in rows:
        if not exists or entry_id in seed_ids:
            continue
        if is_auto and entry_id not in seen_auto:
            seen_auto.add(entry_id)
            auto_entries.append(entry_id)
        elif not is_auto and entry_id not in seen_manual and entry_id not in seen_auto:
            seen_manual.add(entry_id)
            manual_entries.append(entry_id)

    (KB_DIR / ".open_modes_selected").write_text("\n".join(resolved))

    if auto_entries:
        print()
        print("auto_load:")
        for entry_id in auto_entries:
            print(f"  {entry_id}")
    else:
        print("auto: none (all already loaded)")

    if manual_entries:
        print()
        print("Available for selection:")
        half = (len(manual_entries) + 1) // 2
        for i in range(half):
            left = f"  {manual_entries[i]}"
            right = f"  {manual_entries[i+half]}" if i + half < len(manual_entries) else ""
            print(f"{left:<45s}{right}")
    else:
        print("manual: none available")

    con.close()
