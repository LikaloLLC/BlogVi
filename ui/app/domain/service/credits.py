from abc import ABC, abstractmethod


class ICreditsService(ABC):
    @abstractmethod
    def update_or_create(self, customer: str, minutes: float):
        """Update Customer's credits or create"""

    @abstractmethod
    def retrieve(self, customer_id: str):
        """Retrieve Customer's credits '"""

    @abstractmethod
    def minus_credits(self, customer_id: str, minutes: float):
        """Deduct credits from customer's account""" 