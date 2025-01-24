import click

from rich.console import Console
from elog_cli.auth_manager import AuthManager  # Import the AuthManager type
from elog_cli.commands.common import handle_error,manage_http_error  # Import the handle_error function

from elog_cli.elog_management_backend_client.models import ApiResultResponseListLogbookDTO, ApiResultResponseLogbookDTO, LogbookDTO, ShiftDTO, TagDTO, AuthorizationDTO
from elog_cli.elog_management_backend_client.types import Response
from elog_cli.elog_management_backend_client.api.logbooks_controller import get_all_logbook
from elog_cli.elog_management_backend_client.api.logbooks_controller import get_logbook

console = Console()

@click.command()
@click.option("--logbooks", multiple=True, type=str, required=True, help="The name of the logbook.")
@click.pass_context
def show_logbook(ctx, logbooks: list[str]):
    """Show the full information of the logbook."""

    auth_manager: AuthManager = ctx.obj["auth_manager"]  # Retrieve shared AuthManager
    client = auth_manager.get_elog_client()  # Get the authenticated client
    shown = 0
    with client as client:
        all_logbook_result: Response[ApiResultResponseListLogbookDTO] = get_all_logbook.sync_detailed(client=client)
        if all_logbook_result.status_code == 200:
            if all_logbook_result.error_code == 0:
                # Find if we get the name of the logbook in the list
                for log in all_logbook_result.payload:
                    if log.name in logbooks:
                        shown += 1
                        # Fetch the full logbook information using the id
                        full_logbook_result: ApiResultResponseLogbookDTO = get_logbook.sync(client=client, logbook_id=log.id)
                        if full_logbook_result.error_code == 0:
                            log: LogbookDTO = full_logbook_result.payload
                            print_logbook_info(log)
                        else:
                            handle_error(full_logbook_result)
                        if shown == len(logbooks):
                            break
            else:
                handle_error(all_logbook_result)
        else:
            manage_http_error(all_logbook_result)

def print_logbook_info(log: LogbookDTO):
    console.print(f"[bold]Name:[/bold] {log.name}")
    console.print(f"[bold]ID:[/bold] {log.id}")
    console.print(f"[bold]Read All:[/bold] {log.read_all}")
    console.print(f"[bold]Write All:[/bold] {log.write_all}")

    print_shifts(log.shifts)
    print_tags(log.tags)
    print_authorizations(log.authorizations)

def print_shifts(shifts: list[ShiftDTO]):
    shifts_info = " | ".join([f"ID: {shift.id}, Name: shift.name, Start: {shift.from_}, End: {shift.to}" for shift in shifts])
    console.print(f"[bold]Shifts:[/bold] {shifts_info}")

def print_tags(tags: list[TagDTO]):
    tags_info = " | ".join([f"ID: {tag.id}, Name: {tag.name}" for tag in tags])
    console.print(f"[bold]Tags:[/bold] {tags_info}")

def print_authorizations(auth: list[AuthorizationDTO]):
    auth_info = " | ".join([f"ID: {authorization.id}, User: {authorization.owner}, User Type: {authorization.owner_type}, Type: {authorization.authorization_type}, Resource: {authorization.resource}" for authorization in auth])
    console.print(f"[bold]Authorizations:[/bold] {auth_info}")

