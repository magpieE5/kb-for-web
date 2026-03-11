---
id: seed-kb-system
category: seed
title: KB System
updated: '2026-03-11T00:00:00'
---

Markdown-first knowledge base with session continuity for AI coding agents. Single-table schema (knowledge) stored as parquet, rebuilt from markdown on every write. All entries live as `kb/{category}/{id}.md` with YAML frontmatter. Parquet is a queryable cache, never the source of truth.

---

## Core Principle

**Markdown is the sole source of truth.** Parquet is rebuilt from markdown on every write. To create, update, or delete an entry, edit the markdown file and run `kb import_kb`.

---

## Write Operations

**Before creating new entries:**
1. Check working memory — did you just edit something related this session?
2. Search KB — `kb search_kb "topic"` to find existing entries
3. Ask: is this new material, or expansion of existing?

**Creating duplicates is a failure mode.** Always search first.

| Operation | How |
|-----------|-----|
| **Create/Update** | Edit `kb/{category}/{id}.md`, then `kb import_kb` |
| **Delete** | `rm kb/{category}/{id}.md`, then `kb import_kb` |
| **List append** | `kb list_add {id} "content"` (syncs automatically) |
| **List remove** | `kb list_remove {id} "match"` (syncs automatically) |
| **Log session** | `kb log "preview" "handoff" --you-today "..." --me-today "..." --us-today "..."` (syncs automatically) |
| **Extract transcript** | `kb extract_transcript {N}` (syncs automatically) |

---

## Read Operations

| Command | Purpose |
|---------|---------|
| `kb get {id}` | Retrieve full entry content |
| `kb search_kb "query"` | Full-text search with ranked previews |
| `kb list_kb` | List all entries (excludes logs/transcripts) |
| `kb query "SQL"` | SQL against in-memory DuckDB views |

---

## Query

`kb query` runs SQL against in-memory DuckDB views rebuilt from parquet + CSVs each invocation:

- `kb_knowledge` — all KB entries (from kb.parquet)
- `kb_mode` — mode configuration (from kb-mode.csv)
- `kb_mode_config` — mode display order and history depth (from kb-mode-config.csv)
- `kb_todo` — active tasks (from kb-todo.csv)
- `kb_query_log` — query history (from kb-query-log.csv)

**Shell escaping:** Use `<>` instead of `!=` in `kb query` — zsh escapes `!=` before passing to DuckDB.

---

## Session Lifecycle

### Open (trigger: `open-kb`)

Three deterministic commands. The AI iterates with `kb get {id}` for each entry, giving every entry its own tool result frame:

1. `kb open_context` — import markdown, print seed entry IDs (`load:` section), show modes
2. `kb open_mode {selection}` — print auto-load entry IDs (`auto_load:` section), show manual selection list
3. `kb open_select {selection}` — print selected + history entry IDs, show todos

### Close (trigger: `close-kb`)

AI-driven steps (corrections, log, state update), then one deterministic command:

```bash
kb close_context {session_number}
```

This extracts the transcript. Then commit and push — close-kb owns git.

---

## Workflow Configuration

### kb-mode.csv

| Column | Purpose |
|--------|---------|
| mode | Mode name (e.g., `work`, `personal`, `auto`) |
| is_auto | `true` = auto-load on mode selection, `false` = offered for manual selection |
| id | KB entry ID to load |
| load_order | Integer, nullable. Controls load order for seed entries (lower = first, last = strongest recency) |

**Special modes:**
- `seed` — entries loaded for ALL sessions before mode selection
- `auto` — autonomous mode, skips user interaction

### kb-mode-config.csv

| Column | Purpose |
|--------|---------|
| mode | Mode name (must match kb-mode.csv) |
| display_order | Display order in mode selection (lower = first) |
| transcript_depth | How many transcripts to load (0 = none) |
| log_depth | How many session logs to load (0 = none) |

### kb-todo.csv

| Column | Purpose |
|--------|---------|
| todo | Task name |
| is_active | `Y` = show at open-kb, `N` = hidden |
| type | Category (e.g., `work`, `personal`) |
| narrative | Brief status/context |
| mode | Optional link to mode |
| updated | Date last touched |

---

## Schema

Single table: `knowledge`

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PRIMARY KEY | Kebab-case: `{category}-{topic}-{specifics}` |
| category | VARCHAR | Entry type |
| title | VARCHAR | Human-readable title |
| content | TEXT | Full markdown content |
| updated | TIMESTAMP | Last update time |

---

## Entry Format

```markdown
---
id: pattern-example
category: pattern
title: Example Pattern
updated: '2026-02-09T00:00:00'
---

~400 char dense preview for search results.

---

Full structured content below the preview.
```

Categories: reference, pattern, seed, log, transcript, project, decision, issue, other

Start with ~400 char dense preview (key facts, names, relationships), then full structured content. This enables `kb search_kb` to surface relevant entries without loading full content.

---

## Corrections

Accumulator format (no session prefix):
`WRONG: {what} | CORRECTION: {truth} | CONTEXT: {note}`

---

## Environment

Nothing persists between conversations except git-committed files. Every session starts with `./setup.sh` (installs deps, puts `kb` on PATH). Close-kb handles git commit and push.
