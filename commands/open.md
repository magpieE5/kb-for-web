Opens Knowledge Base

# Step 0: Bootstrap

If not already done this session:
```
./setup.sh
```

# Step 1: Load Core Context

```
kb open_context
```

For each ID in the `load:` output, run `kb get {id}` to absorb the entry.

Present the mode list from the command output, then ask:
```
Load which? (e.g., work | all | none)
```

**STOP. Wait for user response.**

# Step 2: Load Mode

```
kb open_mode {user_response}
```

For each ID in the `auto_load:` output, run `kb get {id}` to absorb the entry.

If "Available for selection" appears in the output, **display the list verbatim** — never summarize or omit it — then ask:
```
Load which? (entry IDs | all | none)
```

**STOP. Wait for user response.**

**EXCEPTION: If mode is `auto`, skip to step 3 with `none`.**

# Step 3: Load Selection + History + Todos

```
kb open_select {user_response}
```

For each ID in the `load:` output (if not "none"), run `kb get {id}` to absorb the entry.

For each ID in the `history:` output, run `kb get {id}` to absorb the entry.

Display the todos from the command output.

Session is ready.
