import click
import uvicorn
import sys
from pathlib import Path
from shunollo_core.storage import database

@click.group()
def main():
    """Shunollo CLI - Synesthetic Intelligence Framework"""
    pass

@main.command()
def init_db():
    """Initialize the database schema."""
    click.echo(f"Initializing database at: {database.DB_PATH}")
    try:
        database.create_tables()
        click.echo("[OK] Database initialized.")
    except Exception as e:
        click.echo(f"[FAIL] Failed: {e}")
        sys.exit(1)

    except Exception as e:
        click.echo(f"[FAIL] Failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
