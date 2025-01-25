import click
import json
from httpx import Response

def handle_error(api_error):
    error_message = f"Error: {api_error.error_code}\nMessage: {api_error.error_message}\nError domain: {api_error.error_domain}"
    raise click.ClickException(error_message)

def manage_http_error(response: Response):
    http_status_descriptions = {
        400: "Bad Request: The server could not understand the request due to invalid syntax.",
        401: "Unauthorized: The client must authenticate itself to get the requested response.",
        403: "Forbidden: The client does not have access rights to the content.",
        404: "Not Found: The server can not find the requested resource.",
        500: "Internal Server Error: The server has encountered a situation it doesn't know how to handle.",
        502: "Bad Gateway: The server, while acting as a gateway or proxy, received an invalid response from the upstream server.",
        503: "Service Unavailable: The server is not ready to handle the request.",
        504: "Gateway Timeout: The server, while acting as a gateway or proxy, did not get a response in time from the upstream server."
    }
    
    description = http_status_descriptions.get(response.status_code, "Unknown HTTP Error")
    
    try:
        error_content = json.loads(response.content)
        if isinstance(error_content, dict) and "errorMessage" in error_content:
            description = error_content["errorMessage"]
    except json.JSONDecodeError:
        pass
       
    error_message = f"HTTP Error: {response.status_code}\nDescription: {description}"
    raise click.ClickException(error_message)