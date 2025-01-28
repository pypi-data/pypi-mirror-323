import http.server
import socketserver
import threading
import time
import urllib.parse
import webbrowser
from urllib.parse import urlencode

import click
import requests

from tinybird.tb.modules.cli import CLIConfig, cli
from tinybird.tb.modules.common import coro
from tinybird.tb.modules.feedback_manager import FeedbackManager


class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # The access_token is in the URL fragment, which is not sent to the server
        # We'll send a small HTML page that extracts the token and sends it back to the server
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
        <html>
        <head>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background: #f5f5f5;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                .message {
                    background: white;
                    padding: 2rem 3rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                h1 {
                    color: #25283D;
                    font-size: 1.2rem;
                    margin: 0;
                    font-weight: 500;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>Authenticating...</h1>
            </div>
            <script>
                var hash = window.location.hash.substr(1);
                var access_token = new URLSearchParams(hash).get('access_token');
                window.history.pushState({}, '', '/');
                fetch('/?token=' + access_token, {method: 'POST'})
                    .then(() => {
                        document.querySelector('.message h1').textContent = 'Authentication successful! You can close this window.';
                    });
            </script>
        </body>
        </html>
        """)

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if "token" in query_params:
            token = query_params["token"][0]
            self.server.auth_callback(token)  # type: ignore
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(400, "Missing 'token' parameter")

        self.server.shutdown()

    def log_message(self, format, *args):
        # Suppress log messages
        return


AUTH_SERVER_PORT = 49160


class AuthServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, auth_callback):
        self.auth_callback = auth_callback
        super().__init__(server_address, RequestHandlerClass)


def start_server(auth_callback):
    with AuthServer(("", AUTH_SERVER_PORT), AuthHandler, auth_callback) as httpd:
        httpd.timeout = 30
        start_time = time.time()
        while time.time() - start_time < 60:  # Run for a maximum of 60 seconds
            httpd.handle_request()


@cli.command()
@click.option(
    "--host",
    help="Set custom host if it's different than https://api.tinybird.co. See https://www.tinybird.co/docs/api-reference/overview#regions-and-endpoints for the available list of regions.",
)
@click.option(
    "--workspace",
    help="Set the workspace to authenticate to. If unset, the default workspace will be used.",
)
@coro
async def login(host: str, workspace: str):
    """Authenticate using the browser."""
    auth_event = threading.Event()
    auth_code = [None]  # Using a list to store the code, as it's mutable
    host = host or "https://api.wadus2.gcp.tinybird.co"

    def auth_callback(code):
        auth_code[0] = code
        auth_event.set()

    click.echo(FeedbackManager.highlight(message="» Opening browser for authentication..."))

    # Start the local server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(auth_callback,))
    server_thread.daemon = True
    server_thread.start()

    # Open the browser to the auth page
    if "wadus" in host:
        client_id = "Rpl7Uy9aSjqoPCSvHgGl3zNQuZcSOXBe"
        base_auth_url = "https://auth.wadus1.tinybird.co"
    else:
        client_id = "T6excMo8IKguvUw4vFNYfqlt9pe6msCU"
        base_auth_url = "https://auth.tinybird.co"
    callback_url = f"http://localhost:{AUTH_SERVER_PORT}"
    params = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "response_type": "token",
        "scope": "openid profile email",
    }
    auth_url = f"{base_auth_url}/authorize?{urlencode(params)}"
    webbrowser.open(auth_url)

    # Wait for the authentication to complete or timeout
    if auth_event.wait(timeout=60):  # Wait for up to 60 seconds
        params = {}
        if workspace:
            params["workspace_id"] = workspace
        response = requests.get(  # noqa: ASYNC210
            f"{host}/v0/user/tokens?{urlencode(params)}",
            headers={"Authorization": f"Bearer {auth_code[0]}"},
        )

        data = response.json()
        cli_config = CLIConfig.get_project_config()
        cli_config.set_token(data.get("workspace_token", ""))
        cli_config.set_token_for_host(data.get("workspace_token", ""), host)
        cli_config.set_user_token(data.get("user_token", ""))
        cli_config.set_host(host)

        ws = await cli_config.get_client().workspace_info()
        for k in ("id", "name", "user_email", "user_id", "scope"):
            if k in ws:
                cli_config[k] = ws[k]

        cli_config.persist_to_file()
        click.echo(FeedbackManager.info(message="\nWorkspace: %s" % ws["name"]))
        click.echo(FeedbackManager.info(message="User: %s" % ws["user_email"]))
        click.echo(FeedbackManager.info(message="Host: %s" % host))
        click.echo(FeedbackManager.success(message="\n✓ Authentication successful!"))
    else:
        click.echo(FeedbackManager.error(message="Authentication failed or timed out."))
