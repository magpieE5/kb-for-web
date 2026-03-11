import re
import typer
import yaml
from typing import Annotated
from datetime import datetime, timezone
from commands import KB_DIR
from commands.import_md import _rebuild_parquet

LIST_ADD_HELP = "Add an item to a list-type KB entry. Creates if it doesn't exist."


def _find_md_file(entry_id):
    matches = list(KB_DIR.rglob(f"{entry_id}.md"))
    return matches[0] if matches else None


def list_add(
    id: Annotated[str, typer.Argument(help="Entry ID (e.g., 'accumulator-corrections')")],
    content: Annotated[str, typer.Argument(help="Item content (will be prefixed with '- ')")],
    title: Annotated[str, typer.Option(help="Title for new list (if creating)")] = None,
    category: Annotated[str, typer.Option(help="Category for new list (if creating)")] = "other",
):
    md_file = _find_md_file(id)
    now = datetime.now(timezone.utc)

    if md_file:
        text = md_file.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            fm['updated'] = now.isoformat()
            body = parts[2].rstrip()
            body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*$', '', body, flags=re.DOTALL)
            body = body.rstrip() + f"\n- {content}\n"
            text = "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body
        else:
            text = text.rstrip() + f"\n- {content}\n"
        md_file.write_text(text, encoding='utf-8')
        print(f"added to {id}")
    else:
        t = title or id.replace("-", " ").title()
        fm = {"id": id, "category": category, "title": t, "updated": now.isoformat()}
        md = "---\n" + yaml.dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"
        md += f"# {t}\n\n- {content}\n"
        cat_dir = KB_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        (cat_dir / f"{id}.md").write_text(md, encoding='utf-8')
        print(f"created {id}")

    _rebuild_parquet(quiet=True)
