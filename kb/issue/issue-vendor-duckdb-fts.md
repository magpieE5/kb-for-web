---
id: issue-vendor-duckdb-fts
category: issue
title: Vendor DuckDB FTS Extension for Offline Search
updated: '2026-03-11T00:00:00'
---

DuckDB FTS extension can't be downloaded in Claude Code web sessions (no outbound to extensions.duckdb.org). search_kb has a LIKE fallback but FTS gives ranked BM25 results. Vendor the extension binary so it's always available.

---

## Problem

`kb search_kb` uses DuckDB's full-text search (FTS) extension for BM25-ranked results. The extension must be downloaded from `extensions.duckdb.org` on first use. Claude Code web sessions block this download, so search falls back to unranked LIKE matching.

## Current State

- `commands/search.py` has a try/except — uses FTS when available, falls back to LIKE
- `setup.sh` attempts `INSTALL fts` silently (works locally, no-ops on web)
- Search works either way, but FTS gives better ranked results

## Fix: Vendor the Linux FTS Binary

Run these on a local machine with internet access. The web environment runs **linux_amd64** — your local OS doesn't matter for this step.

### Step 1: Check your DuckDB version

```bash
python -c "import duckdb; print(duckdb.__version__)"
```

Should output `1.4.3` (match `requirements.txt`).

### Step 2: Download the linux_amd64 FTS extension

```bash
mkdir -p vendor/duckdb-extensions
curl -o /tmp/fts.duckdb_extension.gz \
  "https://extensions.duckdb.org/v1.4.3/linux_amd64/fts.duckdb_extension.gz"
gunzip /tmp/fts.duckdb_extension.gz
mv /tmp/fts.duckdb_extension vendor/duckdb-extensions/fts.duckdb_extension
```

Verify it's a real binary (~1-2 MB), not an error page:

```bash
file vendor/duckdb-extensions/fts.duckdb_extension
ls -lh vendor/duckdb-extensions/fts.duckdb_extension
```

### Step 3: Update setup.sh

Replace the existing FTS pre-install line with:

```bash
# Install vendored DuckDB FTS extension for linux_amd64 (Claude Code web)
DUCKDB_VER=$(python -c "import duckdb; print(duckdb.__version__)")
EXT_TARGET="$HOME/.duckdb/extensions/v${DUCKDB_VER}/linux_amd64"
if [ -f "$REPO_DIR/vendor/duckdb-extensions/fts.duckdb_extension" ]; then
    mkdir -p "$EXT_TARGET"
    cp "$REPO_DIR/vendor/duckdb-extensions/fts.duckdb_extension" "$EXT_TARGET/"
fi
```

### Step 4: Test locally

```bash
# Simulate what happens on web — load from vendored path
python -c "
import duckdb
con = duckdb.connect()
con.execute('LOAD fts')
print('FTS loaded successfully')
"
```

### Step 5: Commit

```bash
git add vendor/duckdb-extensions/fts.duckdb_extension setup.sh
git commit -m "Vendor DuckDB FTS extension for offline search"
```

## Notes

- The extension is version-specific. If `requirements.txt` pins a new DuckDB version, re-download the matching extension.
- The binary is ~1-2 MB — acceptable for git.
- Only linux_amd64 is needed (web environment). Local macOS/Windows use network install or the LIKE fallback.
- The LIKE fallback in `search.py` should stay as a safety net regardless.
