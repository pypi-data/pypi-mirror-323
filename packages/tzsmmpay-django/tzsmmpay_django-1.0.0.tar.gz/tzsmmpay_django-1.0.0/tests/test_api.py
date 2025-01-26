import unittest
from tzsmmpay_django.api import TzSmmPayClient

class TestTzSmmPayClient(unittest.TestCase):
    def setUp(self):
        self.client = TzSmmPayClient(api_key="your_test_api_key")

    def test_create_transaction(self):
        """
        Test creating a transaction.
        """
        response = self.client.create_transaction(
            cus_name="John Doe",
            cus_email="john@example.com",
            cus_number="1234567890",
            amount="100.00",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            callback_url="https://example.com/callback"
        )
        self.assertIn("status", response)

    def test_verify_transaction(self):
        """
        Test verifying a transaction.
        """
        response = self.client.verify_transaction(trx_id="test_trx_id")
        self.assertIn("status", response)
