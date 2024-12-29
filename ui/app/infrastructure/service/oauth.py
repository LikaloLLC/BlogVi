from streamlit_oauth import OAuth2Component
from urllib.parse import urljoin

from presentation.auth import OAuth2ComponentAdapter

DEFAULT_SCOPE = 'offline_access'
BUTTON_NAME = 'Authorize'


class OAuthService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_endpoint: str,
        redirect_uri: str,
        authorize_endpoint: str,
        refresh_token_endpoint: str
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self.authorize_endpoint = authorize_endpoint
        self.redirect_uri = redirect_uri
        self._oauth = OAuth2Component(client_id=client_id, client_secret=client_secret, authorize_endpoint=authorize_endpoint,
                                      token_endpoint=token_endpoint, refresh_token_endpoint=refresh_token_endpoint)

    def authorize_button(self):
        """Return authorization URL based on client credentials. offline_access scope is needed to return refresh token."""
        return self._oauth.authorize_button(BUTTON_NAME, redirect_uri=self.redirect_uri, scope=DEFAULT_SCOPE)

    def refresh_token(self, token: str, force: bool = False):
        return self._oauth.refresh_token(token=token, force=force)


class LogtoOauth2ComponentAdapter(OAuth2ComponentAdapter):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        base_url: str,
    ) -> None:
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip('/')
        
        super().__init__(
            client_id,
            client_secret,
            redirect_uri,
            urljoin(base_url, 'oidc/token'),
            urljoin(base_url, 'oidc/auth'),
            urljoin(base_url, 'oidc/token'),
        ) 