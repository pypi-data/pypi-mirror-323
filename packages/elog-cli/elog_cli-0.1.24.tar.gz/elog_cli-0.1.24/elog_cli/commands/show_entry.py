import click
from rich.console import Console
from elog_cli.auth_manager import AuthManager  # Import the AuthManager type
from elog_cli.commands.common import handle_error, manage_http_error  # Import the handle_error and manage_http_error functions

from elog_cli.elog_management_backend_client.models import ApiResultResponseEntryDTO, EntryDTO, AuthorizationCache
from elog_cli.elog_management_backend_client.types import Unset,Response
from elog_cli.elog_management_backend_client.api.entries_controller import get_full

console = Console()

@click.command()
@click.option("--entry-id", type=str, required=True, help="The id of the entry.")
@click.pass_context
def show_entry(ctx, entry_id: str):
    """Show the full information of the entry."""
    auth_manager: AuthManager = ctx.obj["auth_manager"]  # Retrieve shared AuthManager
    client = auth_manager.get_elog_client()  # Get the authenticated client
    with client as client:
        full_entry_result:Response[ApiResultResponseEntryDTO] = get_full.sync_detailed(
            client=client, 
            entry_id=entry_id,
            include_follow_ups=True,
            include_following_ups=True,
            include_history=True,
            include_references=True,
            include_referenced_by=True,
            include_superseded_by=True,
            authorization_cache=AuthorizationCache()
        )
        if full_entry_result.status_code == 200:
            if full_entry_result.parsed.error_code == 0:
                entry: EntryDTO = full_entry_result.parsed.payload
                print_entry_info(entry)
            else:
                handle_error(full_entry_result.parsed)
        else:
            manage_http_error(full_entry_result)

def print_entry_info(entry: EntryDTO):
    console.print(f"[bold]ID:[/bold] {entry.id}")
    console.print(f"[bold]Title:[/bold] {entry.title}")
    console.print(f"[bold]Content:[/bold] {entry.text}")
    console.print(f"[bold]Event At:[/bold] {entry.event_at}")
    console.print(f"[bold]Created At:[/bold] {entry.logged_at}")
    console.print(f"[bold]Author:[/bold] {entry.logged_by}")

    if not isinstance(entry.tags, Unset) and len(entry.tags) > 0:
        console.print(f"[bold]Tags:[/bold] {', '.join(tag.name for tag in entry.tags)}")
    if not isinstance(entry.references, Unset) and len(entry.references) > 0:
        console.print(f"[bold]References:[/bold] {', '.join(ref.id for ref in entry.references)}")
    if not isinstance(entry.referenced_by, Unset) and len(entry.referenced_by) > 0:
        console.print(f"[bold]Referenced By:[/bold] {', '.join(ref.id for ref in entry.referenced_by)}")
    if not isinstance(entry.follow_ups, Unset) and len(entry.follow_ups) > 0:
        console.print(f"[bold]Follow Ups:[/bold] {', '.join(fup.id for fup in entry.follow_ups)}")
    if not isinstance(entry.following_up, Unset) and len(entry.following_up) > 0:
        console.print(f"[bold]Following Up:[/bold] {', '.join(fup.id for fup in entry.following_up)}")
    if not isinstance(entry.history, Unset) and len(entry.history) > 0:
        console.print(f"[bold]History:[/bold] {', '.join(hist.id for hist in entry.history)}")
    if not isinstance(entry.superseded_by, Unset):
        console.print(f"[bold]Superseded By:[/bold] {entry.superseded_by.id}")
    if not isinstance(entry.attachments, Unset) and len(entry.attachments) > 0:
        console.print(f"[bold]Attachments:[/bold] {', '.join(att.file_name for att in entry.attachments)}")