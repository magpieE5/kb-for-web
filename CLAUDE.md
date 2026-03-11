# KB — Knowledge Base CLI

Markdown-first knowledge base with session continuity for AI coding agents.

## Setup

Run `./setup.sh` at the start of each conversation. Nothing persists between conversations except git-committed files.

After setup, `kb` is on PATH.

## Commands

```bash
kb get {id}                    # Retrieve entry by ID
kb search_kb "query"           # Full-text search
kb list_kb                     # List entries
kb query "SQL"                 # SQL against KB views
kb list_add {id} "content"     # Append to list entry
kb list_remove {id} "match"    # Remove from list entry
kb log "preview" "handoff"     # Create session log
kb import_kb                   # Rebuild parquet from markdown
kb session_details             # Show session info
```

## Trigger Words

These are NOT skills or slash commands. Read the command file and follow its instructions directly.

| Trigger | Action |
|---------|--------|
| `open-kb` | Read and follow `./commands/open.md` |
| `close-kb` | Read and follow `./commands/close.md` |
| `audit-kb` | Read and follow `./commands/audit.md` |

## Conventions

- **Markdown is source of truth.** Parquet is a queryable cache rebuilt from markdown.
- After editing `kb/` files, run `kb import_kb` to sync.
- Search before creating entries — duplicates are a failure mode.
- `kb query` uses in-memory DuckDB. Views: `kb_knowledge`, `kb_mode`, `kb_mode_config`, `kb_todo`, `kb_query_log`.
- Use `<>` instead of `!=` in `kb query` (shell escaping).

## KB Entry Format

```markdown
---
id: category-topic-specifics
category: reference
title: Human Readable Title
updated: '2026-01-01T00:00:00'
---

~400 char dense preview for search results.

---

Full structured content.
```

Categories: reference, pattern, seed, log, transcript, project, decision, issue, other

## Corrections

Accumulator format (no session prefix):
`WRONG: {what} | CORRECTION: {truth} | CONTEXT: {note}`
