#!/usr/bin/env bash
set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
pip install -q -r "$REPO_DIR/requirements.txt"

# Install vendored DuckDB FTS extension if available
VENDORED_FTS="$REPO_DIR/vendor/duckdb-extensions/fts.duckdb_extension"
if [ -f "$VENDORED_FTS" ]; then
    DUCKDB_VER=$(python -c "import duckdb; print(duckdb.__version__)")
    EXT_TARGET="$HOME/.duckdb/extensions/v${DUCKDB_VER}/linux_amd64"
    mkdir -p "$EXT_TARGET"
    cp "$VENDORED_FTS" "$EXT_TARGET/"
fi

BIN_DIR="/usr/local/bin"
[ -w "$BIN_DIR" ] || { BIN_DIR="$HOME/.local/bin"; mkdir -p "$BIN_DIR"; }

cat > "$BIN_DIR/kb" << WRAPPER
#!/usr/bin/env bash
cd "$REPO_DIR" && python -m commands.cli "\$@"
WRAPPER
chmod +x "$BIN_DIR/kb"
echo "ready"
