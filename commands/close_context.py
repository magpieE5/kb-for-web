"""Finalize session — extract transcript."""
import typer
from typing import Annotated
from commands.extract_transcript import extract_transcript as _extract_transcript

CLOSE_CONTEXT_HELP = "Finalize session: extract transcript."


def close_context(
    session_number: Annotated[int, typer.Argument(help="Session number to finalize")],
):
    print("--- extract transcript ---")
    _extract_transcript(session_number)
    print(f"\n--- done (S{session_number:03d}) ---")
