import sqlite3

from invoke.context import Context
from invoke.tasks import task
from rich import print


@task
def lint(c: Context) -> None:
    c.run("poetry run ruff check src/smolvault tests", echo=True, pty=True)


@task
def fmt(c: Context) -> None:
    c.run("poetry run ruff format src/smolvault tests", echo=True, pty=True)


@task
def show_table(c: Context) -> None:
    conn = sqlite3.connect("file_metadata.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM filemetadatarecord")
    print(cursor.fetchall())
    conn.close()
