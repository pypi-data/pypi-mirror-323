import sys
import os
import click
import importlib.metadata

# Add project root to sys.path for imports (useful for local development)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elog_cli.auth_manager import AuthManager
from elog_cli.commands.login import login
from elog_cli.commands.create_entry import create_entry
from elog_cli.commands.list_logbooks import list_logbooks
from elog_cli.commands.show_logbook import show_logbook
from elog_cli.commands.show_entry import show_entry
from elog_cli.commands.import_entry import import_entry

@click.group()
@click.version_option(
    importlib.metadata.version("elog_cli"),
    prog_name="ELOG CLI",
    message="%(prog)s Version: %(version)s"
)
@click.pass_context
def cli(ctx):
    """Root CLI for Elog Management."""
    auth_manager = AuthManager()
    ctx.ensure_object(dict)
    ctx.obj["auth_manager"] = auth_manager

# Register all commands
cli.add_command(login)
cli.add_command(show_logbook)
cli.add_command(create_entry)
cli.add_command(list_logbooks)
cli.add_command(show_entry)
cli.add_command(import_entry)

if __name__ == "__main__":
    cli()