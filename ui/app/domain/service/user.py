from abc import ABC, abstractmethod


class IUserService(ABC):
    @abstractmethod
    def get_or_create(self, customer_id: str):
        """Get or Create user"""

    @abstractmethod
    def update(self, customer_id: str, docsie_api_key: str):
        """Update user""" 