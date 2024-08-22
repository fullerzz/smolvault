import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from invoke.context import Context
from invoke.tasks import task
from rich import print


@task
def lint(c: Context) -> None:
    c.run("ruff check src/smolvault tests --config=pyproject.toml", echo=True, pty=True)


@task
def fmt(c: Context) -> None:
    c.run("ruff format src/smolvault tests --config=pyproject.toml", echo=True, pty=True)


@task
def show_table(c: Context) -> None:
    conn = sqlite3.connect("file_metadata.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM filemetadatarecord")
    print(cursor.fetchall())
    conn.close()


@task
def bak_db(c: Context) -> None:
    timestamp = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d_%H:%M:%S")
    c.run(f"cp file_metadata.db file_metadata_{timestamp}.bak.db", echo=True)
