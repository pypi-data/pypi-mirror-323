from .utils import make_request
from .exceptions import AuthenticationError, ValidationError, APIError

class TzSmmPayClient:
    BASE_URL = "https://tzsmmpay.com/api/"

    def __init__(self, api_key):
        """
        Initialize the client with your API key.
        """
        if not api_key:
            raise AuthenticationError("API key is required.")
        self.api_key = api_key

    def create_transaction(self, cus_name, cus_email, cus_number, amount, success_url, cancel_url, callback_url):
        """
        Creates a new transaction.
        """
        url = self.BASE_URL + "payment/create"
        data = {
            "api_key": self.api_key,
            "cus_name": cus_name,
            "cus_email": cus_email,
            "cus_number": cus_number,
            "amount": amount,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "callback_url": callback_url
        }
        return make_request("POST", url, data)

    def verify_transaction(self, trx_id):
        """
        Verifies the status of a transaction using the transaction ID.
        """
        url = self.BASE_URL + "payment/verify"
        data = {"api_key": self.api_key, "trx_id": trx_id}
        return make_request("POST", url, data)
