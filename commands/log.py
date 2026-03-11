import typer
import yaml
from typing import Annotated
from datetime import datetime, timezone
from commands import KB_DIR, connect
from commands.import_md import _rebuild_parquet

LOG_HELP = "Create a session log entry."


def log(
    preview: Annotated[str, typer.Argument(help="Dense searchable summary (~400 chars)")],
    handoff: Annotated[str, typer.Argument(help="Summary for next session")],
    you_today: Annotated[str, typer.Option(help="What I noticed about the user")] = "",
    me_today: Annotated[str, typer.Option(help="Where I helped/struggled")] = "",
    us_today: Annotated[str, typer.Option(help="Notable dynamics this session")] = "",
):
    con = connect()
    try:
        result = con.execute("""
            SELECT COALESCE(MAX(CAST(REPLACE(id, 'session-', '') AS INT)), 0) + 1
            FROM kb_knowledge WHERE id LIKE 'session-%' AND category = 'log'
        """).fetchone()
        session_number = result[0]
    except Exception:
        session_number = 1
    con.close()

    log_id = f"session-{session_number:03d}"
    now = datetime.now(timezone.utc)
    date = now.strftime('%Y-%m-%d')
    title = f"Session {session_number} Log"

    content = f"""# {title}

**Date:** {date}

---

<!-- PREVIEW -->
{preview}
<!-- /PREVIEW -->

---

## Session Witness

**You today:** {you_today}

**Me today:** {me_today}

**Us today:** {us_today}

---

## Handoff

{handoff}
"""

    fm = {"id": log_id, "category": "log", "title": title, "updated": now.isoformat()}
    md = "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + content

    log_dir = KB_DIR / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{log_id}.md").write_text(md, encoding='utf-8')

    _rebuild_parquet(quiet=True)
    print(f"{log_id}")
