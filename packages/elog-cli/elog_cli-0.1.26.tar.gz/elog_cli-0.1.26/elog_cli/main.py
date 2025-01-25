import sys
import os
import click

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
@click.pass_context
def cli(ctx):
    """Root CLI for Elog Management."""
    auth_manager = AuthManager()
    ctx.ensure_object(dict)
    ctx.obj["auth_manager"] = auth_manager
try:
    import importlib.metadata
    version = importlib.metadata.version("elog_cli")
    cli = click.version_option(version, prog_name="ELOG CLI", message="%(prog)s Version: %(version)s")(cli)
except ImportError:
    pass

@cli.command()
@click.pass_context
def completion(ctx):
    """Generate shell completion script."""
    shell = os.environ.get("_ELOG_CLI_COMPLETE", "bash_source")
    if shell == "bash_source":
        click.echo("eval \"$(_ELOG_CLI_COMPLETE=bash_source elog-cli)\"")
    elif shell == "zsh_source":
        click.echo("eval \"$(_ELOG_CLI_COMPLETE=zsh_source elog-cli)\"")
    elif shell == "fish_source":
        click.echo("eval (env _ELOG_CLI_COMPLETE=fish_source elog-cli)")
    else:
        click.echo("Unsupported shell for completion setup.")

# Register all commands
cli.add_command(login)
cli.add_command(show_logbook)
cli.add_command(create_entry)
cli.add_command(list_logbooks)
cli.add_command(show_entry)
cli.add_command(import_entry)

if __name__ == "__main__":
    cli()