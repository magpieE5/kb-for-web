import typer
import os
from typing import Annotated
from commands import KB_DIR

SET_SESSION_HELP = "Set current session number and detect AI agent."


def _detect_agent() -> str:
    if any(k.startswith('CLAUDE') for k in os.environ):
        return "claude"
    if any(k.startswith('GEMINI') for k in os.environ):
        return "gemini"
    return "unknown"


def set_session(
    session: Annotated[int, typer.Argument(help="Session number")],
    agent: Annotated[str, typer.Option(help="Override agent detection")] = None,
):
    detected = agent or _detect_agent()
    marker = KB_DIR / ".session"
    marker.write_text(f"{session}\n{detected}\n")
    print(f"session={session} agent={detected}")
