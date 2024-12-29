import chargebee
from pydantic import EmailStr

DEFAULT_PLAN = 'Early-Launch-USD-Monthly'


class ChargebeeService:

    def __init__(self, api_key: str, site: str):
        chargebee.configure(api_key, site)

    def get_or_create_customer(self, id_: str, email: EmailStr):
        try:
            result = chargebee.Customer.retrieve(id_)
        except chargebee.api_error.InvalidRequestError:
            result = chargebee.Customer.create({
                'id': id_,
                'email': email
            })
            chargebee.Subscription.create_with_items(result.customer.id, {
                'subscription_items': [
                    {
                        'item_price_id': DEFAULT_PLAN,
                    }
                ],
                "auto_collection": "off"
            })
        return result.customer

    def return_self_serve_portal(self, customer_id: str):
        result = chargebee.PortalSession.create({
            "redirect_url": 'https://blogvi.docsie.com/',
            "customer": {
                "id": customer_id
            }
        })
        return result.portal_session.access_url 