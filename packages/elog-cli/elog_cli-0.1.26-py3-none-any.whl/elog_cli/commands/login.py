import click
from elog_cli.auth_manager import AuthManager

@click.command()
@click.option('--login-type', type=click.Choice(['oauth', 'token']), help="Specify the login type.")
@click.pass_context
def login(ctx, login_type):
    """Authenticate using the chosen login type."""
    auth_manager: AuthManager = ctx.obj["auth_manager"]  # Retrieve shared AuthManager
    auth_manager.login(login_type)
    print("Login successful!")

