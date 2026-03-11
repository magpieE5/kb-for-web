"""Extract transcript from session file and upsert to KB."""
import typer
import yaml
from typing import Annotated
from datetime import datetime, timezone
from pathlib import Path
from commands import KB_DIR
from commands.session_details import get_session_details
from commands.import_md import _rebuild_parquet
from commands.extract_exchanges import extract_exchanges, format_exchanges, detect_format

EXTRACT_TRANSCRIPT_HELP = "Extract transcript from session file and upsert to KB."


def extract_transcript(
    session_number: Annotated[int, typer.Argument(help="Session number (e.g., 3 -> transcript-003)")],
    session_path: Annotated[str, typer.Option(help="Override auto-detection with specific file path")] = None,
    no_suppress: Annotated[bool, typer.Option("--no-suppress", help="Keep all content verbatim")] = False,
    max_exchanges: Annotated[int, typer.Option(help="Limit number of exchanges")] = None,
):
    if session_path:
        file_path = Path(session_path)
        if not file_path.exists():
            print(f"error: file not found: {session_path}")
            raise typer.Exit(1)
    else:
        details = get_session_details()
        if not details.get("latest_session"):
            print("error: no session file found. Provide --session-path.")
            raise typer.Exit(1)
        file_path = Path(details["latest_session"])

    fmt = detect_format(file_path)
    exchanges = extract_exchanges(file_path)
    content = format_exchanges(exchanges, max_exchanges, suppress=not no_suppress)

    entry_id = f"transcript-{session_number:03d}"
    title = f"Session {session_number} Transcript"
    now = datetime.now(timezone.utc)

    transcript_dir = KB_DIR / "transcript"
    transcript_file = transcript_dir / f"{entry_id}.md"
    status = "updated" if transcript_file.exists() else "created"

    fm = {"id": entry_id, "category": "transcript", "title": title, "updated": now.isoformat()}
    md = "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"
    md += f"# {title}\n\n{content}\n"

    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_file.write_text(md, encoding='utf-8')

    _rebuild_parquet(quiet=True)
    print(f"{status}: {entry_id} ({len(exchanges)} exchanges, {len(content)} chars, format={fmt})")
