import abc
from typing import Optional
from supabase import Client


CREDITS_TABLE_NAME = 'credits'


class ICreditsRepository:
    @abc.abstractmethod
    def update_or_create(self, customer_id: str, minutes: float) -> str:
        pass

    @abc.abstractmethod
    def retrieve(self, customer_id: str):
        pass

    @abc.abstractmethod
    def minus_credits(self, customer_id: str, minutes: float):
        pass


class CreditsSupabaseRepository(ICreditsRepository):
    def __init__(self, supabase_client: Client):
        self._supabase = supabase_client

    def update_or_create(self, customer_id: str, minutes: float) -> None:
        instance = self._supabase.table(CREDITS_TABLE_NAME).select("*").eq('customer_id', customer_id).execute()
        if not instance.data:
            self._supabase.table(CREDITS_TABLE_NAME).insert({
                'customer_id': customer_id,
                'minutes': minutes,
            }).execute()
        else:
            instance = instance.data[0]
            self._supabase.table(CREDITS_TABLE_NAME).update({'minutes': minutes + instance['minutes']}).eq('customer_id', customer_id).execute()

        return

    def retrieve(self, customer_id: str):
        instance = self._supabase.table(CREDITS_TABLE_NAME).select("*").eq('customer_id', customer_id).execute()
        return instance

    def minus_credits(self, customer_id: str, minutes: float):
        instance = self.retrieve(customer_id).data[0]
        self._supabase.table(CREDITS_TABLE_NAME).update({'minutes': instance['minutes'] - minutes}).eq('customer_id', customer_id).execute() 