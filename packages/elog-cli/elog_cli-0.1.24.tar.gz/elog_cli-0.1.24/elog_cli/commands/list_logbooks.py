import os
import click
from elog_cli.auth_manager import AuthManager  # Import the AuthManager type
from elog_cli.elog_management_backend_client.models import ApiResultResponseListLogbookDTO
from elog_cli.elog_management_backend_client.api.logbooks_controller import get_all_logbook
from elog_cli.commands.common import handle_error  # Import the handle_error function

ENPOINT_URL = os.environ.get("ENPOINT_URL")


# def log_request(request):
#     print(f"Request event hook: {request.method} {request.url} - Waiting for response")

# def log_response(response):
#     request = response.request
#     print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

@click.command()
@click.pass_context
def list_logbooks(ctx):
    """List all logbooks."""
    auth_manager:AuthManager = ctx.obj["auth_manager"]  # Retrieve shared AuthManager
    client = auth_manager.get_elog_client()  # Get the authenticated client
    with client as client:
        all_logbook_result: ApiResultResponseListLogbookDTO = get_all_logbook.sync(client=client)
        if all_logbook_result.error_code == 0:
            logbooks = all_logbook_result.payload
            if logbooks:
                print(", ".join(logbook.name for logbook in logbooks))
            else:
                print("No logbooks found")
        else:
            handle_error(all_logbook_result)