import click
import os
from elog_cli.auth_manager import AuthManager  # Import the AuthManager type
from elog_cli.elog_management_backend_client.types import File
from elog_cli.elog_management_backend_client.models import ApiResultResponseString, NewEntryWithAttachmentBody, NewEntryDTO
from elog_cli.elog_management_backend_client.api.entries_controller_v_2 import new_entry_with_attachment
from elog_cli.commands.common import handle_error  # Import the handle_error function

@click.command()
@click.option("--title", type=str, required=True, help="The title of the entry.")
@click.option("--text", type=str, required=False, help="Optional text for the entry.")
@click.option("--logbooks", multiple=True, type=str, required=True, help="The logbook to add the entry to.")
@click.option("--tags", multiple=True, type=str, required=False, help="Optional tags for the entry.")
@click.option("--attachments",multiple=True, type=str, required=False, help="Optional attachment for the entry.")
@click.pass_context
def create_entry(ctx, title:str, text:str, logbooks:list[str],tags:list[str], attachments:list[str]):
    """Create a new entry with a title, text, and optional tags."""
    tags = [tag for tag in tags if tag]  # Remove empty items
    logbooks = [logbook for logbook in logbooks if logbook]  # Remove empty items
    attachments = [attachment for attachment in attachments if attachment]  # Remove empty items

    click.echo(f"title: {title}")
    click.echo(f"text: {text}")
    click.echo(f"tags: {tags}")  # Now tags is explicitly a list
    auth_manager:AuthManager = ctx.obj["auth_manager"]  # Retrieve shared AuthManager
    client = auth_manager.get_elog_client()  # Get the authenticated client
    with client as client:
        body = NewEntryWithAttachmentBody(
            entry=NewEntryDTO(
                logbooks=logbooks,
                title=title,
                text=text,
                tags=tags
            ),
            files=[
                File(
                    payload=open(attachment, "rb").read(), 
                    file_name=os.path.basename(attachment),  # Extract only the filename
                    mime_type="application/octet-stream"
                )
                for attachment in attachments]
        )
        result: ApiResultResponseString = new_entry_with_attachment.sync(client=client, body=body)
        if result.error_code == 0:
            click.echo(f"New entry created with id{result.payload}")
        else:
            handle_error(result)