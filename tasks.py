import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from invoke.context import Context
from invoke.tasks import task
from rich import print
from rich.table import Table


@task
def lint(c: Context) -> None:
    c.run("ruff check src/smolvault tests --config=pyproject.toml", echo=True, pty=True)


@task
def fmt(c: Context) -> None:
    c.run("ruff format src/smolvault tests --config=pyproject.toml", echo=True, pty=True)


@task
def pip_compile(c: Context) -> None:
    c.run("uv pip compile pyproject.toml -o requirements.txt", echo=True, pty=True)
    output_line_1 = "\n:heavy_check_mark:[bold green] Operation succeeded![/bold green]"
    output_line_2 = (
        ":yin_yang: [bold cyan]requirements.txt[/bold cyan] compiled from [bold blue]pyproject.toml[/bold blue] :robot:"
    )
    print(f"{output_line_1}\n{output_line_2}")


@task
def show_table(c: Context) -> None:
    conn = sqlite3.connect("file_metadata.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM filemetadatarecord")
    print(cursor.fetchall())
    conn.close()


def output_table(title: str, column_names: list[str], rows: list[Any]) -> None:
    table = Table(title=title)
    for column_name in column_names:
        table.add_column(column_name)
    for row in rows:
        table.add_row(*row)
    print(table)


@task
def show_users_table(c: Context) -> None:
    conn = sqlite3.connect("file_metadata.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM userinfo")
    results = cursor.fetchall()
    conn.close()
    rows: list[tuple[str, str, str, str]] = []
    column_names = ["id", "username", "hashed_password", "email", "full_name"]
    print(
        f"[bold cyan]Unformatted results:[/bold cyan]\n[blue]column_names=[/blue][bold purple]{column_names}[/bold purple]\n {results}"
    )
    for result in results:
        rows.append((str(result[0]), result[1], result[2], result[4]))  # noqa: PERF401
    output_table("[bold cyan]Users Table[/bold cyan]", ["id", "username", "hashed_pwd", "name"], rows)


@task
def bak_db(c: Context) -> None:
    timestamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d_%H:%M:%S")
    c.run(f"cp file_metadata.db file_metadata_{timestamp}.bak.db", echo=True)
