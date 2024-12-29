from streamlit_oauth import OAuth2Component


class OAuth2ComponentAdapter:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        token_endpoint: str,
        authorize_endpoint: str,
        refresh_token_endpoint: str
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = token_endpoint
        self.authorize_endpoint = authorize_endpoint
        self.redirect_uri = redirect_uri

        self._oauth = OAuth2Component(client_id=client_id, client_secret=client_secret,
                                      authorize_endpoint=authorize_endpoint,
                                      token_endpoint=token_endpoint, refresh_token_endpoint=refresh_token_endpoint)

    def authorize_button(self, name: str, scope: str = 'offline_access', key: str | None = None):
        """Return authorization URL based on client credentials.

        offline_access scope is needed to return refresh token.
        """

        return self._oauth.authorize_button(name, redirect_uri=self.redirect_uri, scope=scope, key=key)

    def refresh_token(self, token: str, force: bool = False):
        return self._oauth.refresh_token(token=token, force=force) 