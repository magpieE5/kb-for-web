import typer
import duckdb
from typing import Annotated
from commands import PARQUET_PATH

SEARCH_HELP = "Full-text search across KB entries. Returns ranked results with previews."


def search_kb(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option(help="Max results")] = 10,
):
    con = duckdb.connect()
    con.execute("INSTALL fts; LOAD fts;")
    con.execute(f"CREATE TABLE knowledge AS SELECT * FROM read_parquet('{PARQUET_PATH}')")
    con.execute("PRAGMA create_fts_index('knowledge', 'id', 'title', 'content', overwrite=1)")
    safe_query = query.replace("'", "''")
    rows = con.execute(f"""
        SELECT id, LEFT(content, 200) as preview,
               fts_main_knowledge.match_bm25(id, '{safe_query}') AS score
        FROM knowledge
        WHERE score IS NOT NULL AND category <> 'transcript'
        ORDER BY score DESC LIMIT {limit}
    """).fetchall()
    con.close()
    for row in rows:
        print(f"{row[0]}")
        print(f"  {row[1][:200]}")
        print()
