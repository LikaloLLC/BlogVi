from abc import ABC, abstractmethod
from typing import Optional
from supabase import Client
from infrastructure.service.supabase_service import supabase


USERS_TABLE_NAME = 'users'


class IUserRepository(ABC):
    @abstractmethod
    def create(self, customer_id: str, docsie_api_key: str | None = None):
        """Create User"""

    @abstractmethod
    def retrieve(self, customer_id: str):
        """Retrieve User"""

    @abstractmethod
    def update(self, customer_id: str, docsie_api_key: str | None = None):
        """Update User"""


class UserSupabaseRepository(IUserRepository):
    def __init__(self, supabase_client: Client):
        self._supabase = supabase_client

    def create(self, customer_id: str, docsie_api_key: str | None = None):
        instance = self._supabase.table(USERS_TABLE_NAME).insert({
            'customer_id': customer_id,
            'docsie_api_key': docsie_api_key,
        }).execute()
        return instance

    def retrieve(self, customer_id: str):
        instance = self._supabase.table(USERS_TABLE_NAME).select("*").eq('customer_id', customer_id).execute()
        return instance

    def update(self, customer_id: str, docsie_api_key: str | None = None):
        instance = (self._supabase.table(USERS_TABLE_NAME).update({'docsie_api_key': docsie_api_key}).
                    eq('customer_id', customer_id).execute())
        return instance
