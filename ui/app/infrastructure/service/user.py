from domain.service.user import IUserService
from repositories.user import IUserRepository


class UserService(IUserService):

    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def get_or_create(self, customer_id: str):
        user = self._user_repo.retrieve(customer_id)

        if not user.data:
            user = self._user_repo.create(customer_id)

        return user.data[0]

    def update(self, customer_id: str, docsie_api_key: str):
        return self._user_repo.update(customer_id, docsie_api_key)
