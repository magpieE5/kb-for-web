"""Session detection for AI coding agents (Claude Code, Gemini CLI)."""
import typer
import platform
from pathlib import Path
from datetime import datetime
from commands import ROOT, PARQUET_PATH


def _get_next_session_number() -> int:
    if not PARQUET_PATH.exists():
        return 1
    try:
        import duckdb
        con = duckdb.connect()
        result = con.execute(f"""
            SELECT MAX(CAST(REGEXP_EXTRACT(id, 'session-([0-9]+)', 1) AS INT))
            FROM read_parquet('{PARQUET_PATH}')
            WHERE category = 'log' AND id LIKE 'session-%'
        """).fetchone()
        con.close()
        return (result[0] if result and result[0] else 0) + 1
    except Exception:
        return 1


def _find_claude_session(home, encoded_path):
    claude_projects = home / '.claude' / 'projects' / encoded_path
    if not claude_projects.exists():
        return None
    jsonls = sorted(
        [j for j in claude_projects.glob('*.jsonl') if 'agent' not in j.name],
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    return jsonls[0] if jsonls else None


def _find_gemini_session(home):
    gemini_tmp = home / '.gemini' / 'tmp'
    if not gemini_tmp.exists():
        return None
    all_chats = []
    for project_dir in gemini_tmp.iterdir():
        if project_dir.is_dir():
            chats_dir = project_dir / 'chats'
            if chats_dir.exists():
                all_chats.extend(chats_dir.glob('*.json'))
    if not all_chats:
        return None
    all_chats.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return all_chats[0]


def get_session_details() -> dict:
    home = Path.home()
    system = platform.system()
    encoded = str(ROOT).replace('\\', '-').replace(':', '-') if system == 'Windows' else str(ROOT).replace('/', '-')

    claude_session = _find_claude_session(home, encoded)
    gemini_session = _find_gemini_session(home)

    client = 'unknown'
    latest_session = None
    claude_mtime = claude_session.stat().st_mtime if claude_session else 0
    gemini_mtime = gemini_session.stat().st_mtime if gemini_session else 0

    if claude_mtime > gemini_mtime and claude_session:
        client, latest_session = 'claude', str(claude_session)
    elif gemini_session:
        client, latest_session = 'gemini', str(gemini_session)
    elif claude_session:
        client, latest_session = 'claude', str(claude_session)

    return {
        'session_number': _get_next_session_number(),
        'date_display': datetime.now().strftime('%a %b %d %H:%M:%S %Y'),
        'client': client,
        'latest_session': latest_session,
    }


SESSION_DETAILS_HELP = "Show session details (date, session number, client)."


def session_details(
    field: str = typer.Argument(None, help="Specific field (e.g., session_number, date_display). Omit for all."),
):
    details = get_session_details()
    if field:
        if field not in details:
            typer.echo(f"Unknown: {field}. Available: {', '.join(details.keys())}")
            raise typer.Exit(1)
        typer.echo(details[field])
    else:
        for k, v in details.items():
            typer.echo(f"{k}: {v}")
