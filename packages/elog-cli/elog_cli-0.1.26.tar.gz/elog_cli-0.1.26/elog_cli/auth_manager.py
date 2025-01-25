import json
import os
from elog_cli.oauth_login import OAuthDeviceCodeFlow
from elog_cli.token_login import TokenLogin
from elog_cli.elog_management_backend_client.client import AuthenticatedClient

# Define OAuth2 endpoints and client details
CODE_FLOW_SERVER_URL = os.environ.get("ELOG_CLI_CODE_FLOW_SERVER_URL")
TOKEN_URL = os.environ.get("ELOG_CLI_TOKEN_URL")
CLIENT_ID = os.environ.get("ELOG_CLI_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ELOG_CLI_CLIENT_SECRET")
ENPOINT_URL = os.environ.get("ELOG_CLI_ENPOINT_URL")

class AuthManager:
    def __init__(self, token_file=".elog_cli/token_data.json"):
        self.client = None
        self.token_file = os.path.join(os.path.expanduser("~"), token_file)
        self.token_data = self.load_token_data()
        self.token_type = self.token_data.get("login_type") if self.token_data else None

        if self.token_type == "oauth":
            self.auth_flow = OAuthDeviceCodeFlow(CLIENT_ID, CLIENT_SECRET, CODE_FLOW_SERVER_URL, TOKEN_URL)
        elif self.token_type == "token":
            self.auth_flow = TokenLogin()
        else:
            self.auth_flow = None

    def load_token_data(self):
        """Load token data from disk."""
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as file:
                return json.load(file)
        return None

    def save_token_data(self):
        """Save token data to disk."""
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
        with open(self.token_file, "w") as file:
            json.dump(self.token_data, file)

    def login(self, login_type=None):
        """Perform the login flow based on the token type."""
        if not self.auth_flow or login_type:
            self.token_type = login_type or input("Please choose your login type (oauth/token): ").strip().lower()
            if self.token_type == "oauth":
                self.auth_flow = OAuthDeviceCodeFlow(CLIENT_ID, CLIENT_SECRET, CODE_FLOW_SERVER_URL, TOKEN_URL)
            elif self.token_type == "token":
                self.auth_flow = TokenLogin()
            else:
                raise ValueError("Invalid login type specified")

        self.token_data = self.auth_flow.login()
        self.token_data["login_type"] = self.token_type  # Add login type to token data
        self.save_token_data()

    def authenticate(self):
        """Authenticate and manage the token data."""
        if not self.token_data:
            self.token_data = self.auth_flow.login(self)
        else:
            self.token_data = self.auth_flow.check_and_refresh_token(self.token_data)
        self.token_data["login_type"] = self.token_type  # Ensure login type is in token data
        self.save_token_data()

    def get_access_token(self):
        """Get the current access token."""
        self.authenticate()
        return self.token_data["access_token"]

    def save_token(self, token_data):
        """Save token data to disk."""
        self.token_data = token_data
        self.token_data["login_type"] = self.token_type  # Ensure login type is in token data
        self.save_token_data()

    def get_elog_client(self) -> AuthenticatedClient:
        if self.client is None:
            self.client = AuthenticatedClient(
                base_url=ENPOINT_URL, 
                token=self.get_access_token(),
                prefix="",
                auth_header_name="x-vouch-idp-accesstoken",
                # httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}}
            )
        return self.client
