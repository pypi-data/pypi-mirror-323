import http.server
import socketserver
import webbrowser
import requests
import urllib.parse
import base64
import os
import hashlib
import time

REDIRECT_PATH = "/callback"

############################
# 2. PKCE Helper Functions #
############################
def generate_pkce_pair():
    """Generate a code_verifier and code_challenge for PKCE."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("utf-8")).digest()
    ).decode("utf-8").rstrip("=")
    return code_verifier, code_challenge


##########################
# 3. Local HTTP Server   #
##########################
class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """
    Simple handler to capture the OAuth2 redirect with `code` and store it for our main flow.
    """

    # We'll store the authorization code as a class variable for simplicity
    auth_code = None
    error = None

    def do_GET(self):
        # Parse the query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == REDIRECT_PATH:
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if "error" in query_params:
                # The user may have denied consent or something went wrong
                OAuthCallbackHandler.error = query_params["error"][0]
                self._send_response("Error during authorization flow. Check terminal.")
            elif "code" in query_params:
                OAuthCallbackHandler.auth_code = query_params["code"][0]
                self._send_response("Authentication successful. You can close this window.")
            else:
                self._send_response("No code found in the query parameters.")
        else:
            self._send_response("Invalid callback path.")

    def _send_response(self, message):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


def start_local_server(REDIRECT_HOST, REDIRECT_PORT):
    """Start a local server to handle the OAuth callback."""
    handler = OAuthCallbackHandler
    httpd = socketserver.TCPServer((REDIRECT_HOST, REDIRECT_PORT), handler)
    return httpd

def refresh_access_token(refresh_token, CLIENT_ID, TOKEN_ENDPOINT):
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token
    }
    resp = requests.post(TOKEN_ENDPOINT, data=data)
    if resp.status_code == 200:
        token_json = resp.json()
        return token_json
    else:
        raise Exception(f"Refresh failed: {resp.status_code}, {resp.text}")

# Check if we are within 60 seconds of expiry
def needs_refresh(tokens):
    now = time.time()
    expires_in = tokens.get("expires_in")
    obtained_at = tokens.get("obtained_at")
    # If we're near expiration (e.g. within 60 seconds), refresh
    return now >= obtained_at + expires_in - 60


##################################
# PKCE method for Azure Entra ID #
##################################
def retrieve_tokens_AZURE_pkce(TENANT_ID = "", CLIENT_ID = "", KDB_SCOPE = "", tokens = {}, REDIRECT_PORT = 5000):
    ###################
    #  Configuration  #
    ###################
    REDIRECT_HOST = "localhost"
    REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}{REDIRECT_PATH}"
    # Scopes your app needs ("openid profile offline_access" to get an ID token and refresh token)
    SCOPES = [
        "openid",
        "profile",
        "offline_access",
        KDB_SCOPE
    ]
    # Azure Entra ID (Azure AD) Endpoints
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    AUTHORIZE_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
    TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"

    #check if we already have tokens, and if they are expired, retrieve new tokens using the refresh token
    if tokens:
        if needs_refresh(tokens):
            # Perform the refresh
            new_tokens = refresh_access_token(tokens["refresh_token"], CLIENT_ID, TOKEN_ENDPOINT)
            tokens["access_token"] = new_tokens["access_token"]
            tokens["refresh_token"] = new_tokens.get("refresh_token", tokens["refresh_token"])
            tokens["expires_in"] = new_tokens["expires_in"]
            tokens["obtained_at"] = time.time()

        return tokens

    # Generate PKCE code verifier and challenge
    code_verifier, code_challenge = generate_pkce_pair()

    # Build the authorization URL
    # See MS docs for all optional query parameters:
    # https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(SCOPES),         # space-separated
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{AUTHORIZE_ENDPOINT}?{urllib.parse.urlencode(params)}"

    # Spin up local server
    httpd = start_local_server(REDIRECT_HOST, REDIRECT_PORT)

    # Open browser to Azure login
    print("Opening browser to authenticate...")
    webbrowser.open(auth_url)

    # Wait for the callback to set the auth_code or error
    print(f"Listening on {REDIRECT_URI} for the authorization response...")
    OAuthCallbackHandler.auth_code = None
    OAuthCallbackHandler.error = None
    while OAuthCallbackHandler.auth_code is None and OAuthCallbackHandler.error is None:
        httpd.handle_request()

    # We can now shut down the server
    httpd.server_close()

    # Check if there was an error
    if OAuthCallbackHandler.error:
        print("Error from authorization server:", OAuthCallbackHandler.error)
        return

    # Exchange the auth_code for an access token
    auth_code = OAuthCallbackHandler.auth_code
    print("Authorization code received. Exchanging for tokens...")

    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
        "scope": " ".join(SCOPES),
    }
    token_response = requests.post(TOKEN_ENDPOINT, data=data)
    if token_response.status_code == 200:
        tokens = token_response.json()
        return { "access_token": tokens.get("access_token"),
                 "refresh_token": tokens.get("refresh_token"),
                 "expires_in": tokens.get("expires_in"),
                 "obtained_at": time.time()
        }
    
    else:
        raise Exception(f"Failed to exchange code for tokens. Status code: {token_response.status_code}, Response: {token_response.text}")


################################################
# client credentials method for Azure Entra ID #
################################################
def retrieve_tokens_AZURE_client_credentials(TENANT_ID = "", CLIENT_ID = "", CLIENT_SECRET = "", KDB_SCOPE = "", tokens = {}):
    #check if we already have tokens, and if they are expired, retrieve new tokens using the refresh token
    if tokens and not needs_refresh(tokens):
        return tokens
    
    TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": KDB_SCOPE
    })
    
    if resp.status_code == 200:
        token_json = resp.json()
        return { "access_token": token_json["access_token"],
                 "expires_in": token_json["expires_in"],
                 "obtained_at": time.time()
        }
    
    else:
        raise Exception(f"Client credentials flow failed: {resp.status_code}, {resp.text}")
