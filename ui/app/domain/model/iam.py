from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import NewType

import requests
from phonenumbers import PhoneNumber
from pydantic import AliasGenerator, BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from pydantic.alias_generators import to_camel
from pydantic_extra_types.phone_numbers import PhoneNumber

OrganizationId = NewType('OrganizationId', str)
RoleId = NewType('RoleId', str)
MemberId = NewType('MemberId', str)
UserId = NewType('UserId', str)


class User(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel
        )
    )

    id: UserId
    username: str | None = None

    name: str | None
    primary_email: EmailStr
    primary_phone: PhoneNumber | None
    avatar: HttpUrl | None

    last_sign_in_at: datetime | None
    created_at: datetime
    updated_at: datetime

    is_suspended: bool


class IdToken(BaseModel):
    iss: str
    sub: str
    iat: datetime
    exp: datetime
    aud: str
    at_hash: str
    created_at: datetime
    updated_at: datetime
    email: EmailStr
    username: str | None = None
    name: str | None = None
    picture: str | None = None
    roles: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    organization_roles: list[str] = Field(default_factory=list)
    email_verified: bool | None = None


class Organization(BaseModel):
    id: OrganizationId
    name: str

    def __str__(self):
        return self.name


class Role(BaseModel):
    id: RoleId
    name: str


class Member(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel
        )
    )

    id: MemberId
    username: str

    name: str | None
    primary_email: EmailStr | None
    primary_phone: PhoneNumber | None
    avatar: HttpUrl | None

    last_sign_in_at: datetime | None
    created_at: datetime
    updated_at: datetime

    is_suspended: bool

    roles: list[Role] = Field(validation_alias='organizationRoles')


class IIdpUserService(ABC):
    """ACL to communicate with Identity provider."""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User:
        """Get user by ID."""


class ITokenService(ABC):
    """ACL to decode tokens."""

    def __init__(self, openid_conf_endpoint: str):
        self.openid_configuration = requests.get(openid_conf_endpoint).json()

    @abstractmethod
    def decode_id_token(
        self,
        id_token: str,
        verify_exp: bool = False,
        verify_iss: bool = False
    ) -> IdToken:
        """Decode an ID token."""


class IIdpOrganizationService(ABC):
    """ACL to communicate with Identity provider."""

    @abstractmethod
    def get_by_id(self, id: OrganizationId) -> Organization:
        """Get an organization by ID."""

    @abstractmethod
    def create(self, tenant_id: str, name: str) -> Organization:
        """Create an organization."""

    @abstractmethod
    def add_members(self, organization_id: OrganizationId, member_ids: list[UserId]) -> None:
        """Add members to an organization."""

    @abstractmethod
    def list_members(self, organization_id: OrganizationId) -> list[Member]:
        """List members of an organization."""

    @abstractmethod
    def organizations_of_user(self, user_id: UserId) -> list[Organization]:
        """Get all organizations of user""" 