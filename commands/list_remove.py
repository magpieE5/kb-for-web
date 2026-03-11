import re
import typer
import yaml
from typing import Annotated
from datetime import datetime, timezone
from commands import KB_DIR
from commands.import_md import _rebuild_parquet

LIST_REMOVE_HELP = "Remove an item from a list-type KB entry by matching text (case-insensitive)."


def _find_md_file(entry_id):
    matches = list(KB_DIR.rglob(f"{entry_id}.md"))
    return matches[0] if matches else None


def list_remove(
    id: Annotated[str, typer.Argument(help="Entry ID")],
    match: Annotated[str, typer.Argument(help="Text to match (case-insensitive substring)")],
):
    md_file = _find_md_file(id)
    if not md_file:
        print(f"not found: {id}")
        raise typer.Exit(1)

    text = md_file.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) < 3:
        print(f"invalid frontmatter: {id}")
        raise typer.Exit(1)

    fm = yaml.safe_load(parts[1])
    body = parts[2]
    body_clean = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*$', '', body, flags=re.DOTALL)

    lines = body_clean.split('\n')
    removed = None
    new_lines = []
    for line in lines:
        if removed is None and line.strip().startswith('- ') and match.lower() in line.lower():
            removed = line.strip()
        else:
            new_lines.append(line)

    if removed is None:
        print(f"no item matching '{match}'")
        raise typer.Exit(1)

    fm['updated'] = datetime.now(timezone.utc).isoformat()
    new_text = "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + '\n'.join(new_lines)
    md_file.write_text(new_text, encoding='utf-8')

    _rebuild_parquet(quiet=True)
    print(f"removed: {removed}")
