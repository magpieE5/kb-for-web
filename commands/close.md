Closes Knowledge Base

Save session log, update state, finalize, commit, push.

## Workflow

### 0. Get Date

```bash
kb session_details date_display
```

### 1. Corrections

If corrections this session:
```bash
kb list_add accumulator-corrections "WRONG: ... | CORRECTION: ... | CONTEXT: ..."
```

### 2. Log Session

```bash
kb log "preview" "handoff" --you-today "..." --me-today "..." --us-today "..."
```

- **preview**: ~400 char dense summary. Format: `{date} ({day}), {mode}. {Key events}. Key: {terms}.`
- **handoff**: Summary for next session. Unfinished business, context needed.
- **witness** options:
  - `--you-today`: What I noticed about the user
  - `--me-today`: Where I helped/struggled
  - `--us-today`: Notable dynamics this session

Note the returned session ID (e.g., `session-003`) — extract the number for step 4.

### 3. Update State

Edit `kb/seed/state.md` (the markdown file on disk).

Update:
- Relationship: temperature, trajectory, friction, last note
- Attention: current focus areas
- Threads: active and unresolved

### 4. Finalize

```bash
kb close_context {session_number}
```

This extracts the transcript.

### 5. Commit & Push

```bash
git add -A && git commit -m "S{N}: {description}" && git push
```

A GitHub Action auto-merges the `claude/*` branch to main after push. The user deletes the Claude Code Web session after this completes.
