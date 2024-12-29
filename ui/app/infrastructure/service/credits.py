from dependency_injector.wiring import Provider

from domain.service.credits import ICreditsService
from repositories.credits import ICreditsRepository


class CreditsService(ICreditsService):
    def __init__(self, credits_repo: ICreditsRepository = Provider['credits_repository']):
        self.credits_repo = credits_repo

    def update_or_create(self, customer: str, minutes: float):
        return self.credits_repo.update_or_create(customer, minutes)

    def retrieve(self, customer_id: str):
        return self.credits_repo.retrieve(customer_id)

    def minus_credits(self, customer_id: str, minutes: float):
        return self.credits_repo.minus_credits(customer_id, minutes) 