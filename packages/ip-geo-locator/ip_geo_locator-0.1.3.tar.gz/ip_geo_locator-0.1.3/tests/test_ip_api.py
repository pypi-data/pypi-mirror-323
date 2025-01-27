import unittest
from ip_geo_locator.ip_api import IPApiService

class TestIPApiService(unittest.TestCase):
    """
    Unit tests for the IPApiService class.
    """

    def setUp(self):
        """
        Setup for tests.
        """
        self.valid_api_key = "test_api_key"  # Use a dummy API key for testing
        self.valid_ip = "125.161.79.09"
        self.invalid_ip = ""

    def test_api_key_required(self):
        """
        Test that API key is required during initialization.
        """
        with self.assertRaises(ValueError):
            IPApiService(api_key=None)

    def test_ip_address_required(self):
        """
        Test that IP address is required for fetching IP information.
        """
        service = IPApiService(api_key=self.valid_api_key)
        with self.assertRaises(ValueError):
            service.get_ip_info(self.invalid_ip)

    def test_valid_request(self):
        """
        Test a valid API call.
        """
        service = IPApiService(api_key=self.valid_api_key)
        response = service.get_ip_info(self.valid_ip)
        self.assertIsInstance(response, dict)

    # def test_invalid_request(self):
    #     """
    #     Test with an invalid IP and handle gracefully.
    #     """
    #     service = IPApiService(api_key=self.valid_api_key)
    #     response = service.get_ip_info("invalid_ip")
    #     self.assertIsNone(response)

if __name__ == "__main__":
    unittest.main()
