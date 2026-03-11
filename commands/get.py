import typer
from typing import Annotated
from commands import connect

GET_HELP = "Retrieve a KB entry by ID."


def get(id: Annotated[str, typer.Argument(help="KB entry ID")]):
    con = connect()
    row = con.execute("SELECT content FROM kb_knowledge WHERE id = ?", [id]).fetchone()
    con.close()
    if row:
        print(row[0])
