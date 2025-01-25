import click
import os
from elog_cli.auth_manager import AuthManager  # Import the AuthManager type
from elog_cli.elog_management_backend_client.types import File,Response
from elog_cli.elog_management_backend_client.models import ApiResultResponseString, NewEntryWithAttachmentBody, NewEntryDTO
from elog_cli.elog_management_backend_client.api.entries_controller_v_2 import new_entry_with_attachment
from elog_cli.commands.common import handle_error, manage_http_error  # Import the handle_error and manage_http_error functions

@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def import_entry(ctx, file_path: str):
    """Create a new entry with a title, text, and optional tags."""
    title:str = ""
    text:str = ""
    tags: list[str] = []
    logbooks: list[str] = []
    attachments: list[str] = []

    # open the file and check if the file is json or xml
    with open(file_path, "r") as file:
        lines = file.readlines()
        if file_path.endswith(".xml"):
            import xml.etree.ElementTree as ET
            root = ET.fromstring("".join(lines))
            title = root.find("title").text if root.find("title") is not None else ""
            text = root.find("text").text if root.find("text") is not None else ""
            tags = [tag.text for tag in root.findall("segment")] if root.find("segment") is not None else []
            logbooks = [logbook.text for logbook in root.findall("logbook")] if root.find("logbook") is not None else []
            attachments = [attachment.text for attachment in root.findall("attachment")] if root.find("attachment") is not None else []
        else:
            click.echo(f"Unsupported file format: {file_path}")
            return

    # Sanitize attachments
    base_path = os.path.dirname(file_path)
    sanitized_attachments = [
        os.path.join(base_path, attachment) if not os.path.isabs(attachment) else attachment
        for attachment in attachments
    ]

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
                for attachment in sanitized_attachments]
        )
        result: Response[ApiResultResponseString] = new_entry_with_attachment.sync_detailed(client=client, body=body)
        if result.status_code == 200 or result.status_code == 201:
            if result.parsed.error_code == 0:
                entry_id: ApiResultResponseString = result.parsed.payload
                click.echo(f"Entry created with ID: {entry_id}")
            else:
                handle_error(result.parsed)
                return 1
        else:
            manage_http_error(result)
            return 1