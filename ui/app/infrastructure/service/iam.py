from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urljoin

import jwt
import requests
from jwt import PyJWKClient, PyJWKClientConnectionError
from pydantic import TypeAdapter

from domain.model.iam import (
    IIdpOrganizationService,
    IIdpUserService,
    ITokenService,
    IdToken,
    Member,
    Organization,
    OrganizationId,
    User,
    UserId,
)

OrganizationList = TypeAdapter(list[Organization])
MemberList = TypeAdapter(list[Member])


class LogtoAPIClient:
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ):
        self._base_url = base_url
        self._client_id = client_id
        self._client_secret = client_secret

        self._token_response = None
        self._token_requested_at: datetime | None = None

    def get(self, endpoint: str, *, params: dict | None = None):
        return self.request(endpoint, "GET", params=params)

    def post(self, endpoint: str, *, payload: dict | None = None, params: dict | None = None):
        return self.request(endpoint, "POST", payload=payload, params=params)

    def delete(self, endpoint: str):
        return self.request(endpoint, "DELETE")

    def request(
        self,
        endpoint: str,
        method: str,
        *,
        payload: dict | None = None,
        params: dict | None = None,
    ) -> dict | list[dict]:
        url = self._get_endpoint_url(endpoint)
        access_token = self._get_token()

        response = requests.request(
            method,
            url,
            headers={'Authorization': f'Bearer {access_token}'},
            json=payload,
            params=params
        )
        response.raise_for_status()

        # It returns non-json responses even if they are successful for some endpoints
        try:
            return response.json()
        except json.JSONDecodeError:
            return {}

    def _get_token(self) -> str:
        if (
            self._token_response is None
            or timedelta(seconds=self._token_response['expires_in']) + self._token_requested_at >= datetime.now()
        ):
            self._token_response = self._request_token()
            self._token_requested_at = datetime.now()

        return self._token_response['access_token']

    def _request_token(self) -> dict:
        return requests.post(
            urljoin(self._base_url, '/oidc/token/'),
            auth=(self._client_id, self._client_secret),
            data={
                'grant_type': 'client_credentials',
                'resource': f'https://default.logto.app/api',
                'scope': 'all',
            }
        ).json()

    def _get_endpoint_url(self, endpoint: str) -> str:
        if self._base_url.endswith('/'):
            base_url = self._base_url
        else:
            base_url = self._base_url + '/'

        return urljoin(base_url, endpoint)


class LogtoUserService(IIdpUserService):
    def __init__(self, client: LogtoAPIClient):
        self.client = client

    def get_by_id(self, user_id: UserId) -> User:
        response = self.client.get(f'/api/users/{user_id}')

        return User.model_validate(response)


class TokenService(ITokenService):
    def __init__(self, openid_conf_endpoint: str):
        self.openid_configuration = requests.get(openid_conf_endpoint).json()

    def decode_id_token(
        self,
        id_token: str,
        verify_exp: bool = False,
        verify_iss: bool = False
    ) -> IdToken:
        jwks_client = CustomPyJWKClient(self.openid_configuration['jwks_uri'], max_cached_keys=512)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token).key

        payload = jwt.decode(
            id_token,
            signing_key,
            algorithms=self.openid_configuration['id_token_signing_alg_values_supported'],
            issuer=self.openid_configuration['issuer'],
            options={'verify_exp': verify_exp, 'verify_aud': False, 'verify_iss': verify_iss},
            leeway=300  # Add 5 minutes of leeway for clock skew
        )

        return IdToken.model_validate(payload)


class CustomPyJWKClient(PyJWKClient):
    def fetch_data(self) -> Any:
        jwk_set: Any = None

        try:
            jwk_set = requests.get(
                self.uri,
                headers=self.headers,
                timeout=self.timeout,
            ).json()
        except (requests.exceptions.RequestException, TimeoutError) as e:
            msg = f'Fail to fetch data from the url, err: "{e}"'
            raise PyJWKClientConnectionError(msg)
        else:
            return jwk_set
        finally:
            if self.jwk_set_cache is not None:
                self.jwk_set_cache.put(jwk_set)


class LogtoOrganizationService(IIdpOrganizationService):
    def __init__(self, client: LogtoAPIClient):
        self.client = client

    def get_by_id(self, id: OrganizationId) -> Organization:
        response = self.client.get(f'api/organizations/{id}')

        return Organization.model_validate(response)

    def create(self, tenant_id: str, name: str) -> Organization:
        response = self.client.post(
            'api/organizations',
            payload={
                'tenant_id': tenant_id,
                'name': name,
            },
        )

        return Organization.model_validate(response)

    def add_members(self, organization_id: OrganizationId, member_ids: list[UserId]) -> None:
        self.client.post(
            f'api/organizations/{organization_id}/users',
            payload={
                'userIds': member_ids
            }
        )

    def list_members(self, organization_id: OrganizationId) -> list[Member]:
        response = self.client.get(f'api/organizations/{organization_id}/users')

        return MemberList.validate_python(response)

    def organizations_of_user(self, user_id: UserId) -> list[Organization]:
        response = self.client.get(f'/api/users/{user_id}/organizations')

        return OrganizationList.validate_python(response) 