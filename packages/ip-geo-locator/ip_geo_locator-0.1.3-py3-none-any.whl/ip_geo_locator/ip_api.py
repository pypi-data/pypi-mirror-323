import requests

class IPApiService:
    """
    A Python wrapper for an IP API service with compulsory IP and API key validation.
    """
    def __init__(self, base_url="https://api.leafslice.com/ip", api_key=None):
        if not api_key:
            raise ValueError("API key is required to use this service.")
        self.base_url = base_url
        self.api_key = api_key

    def get_ip_info(self, ip_address):
        """
        Fetch IP information from the API.

        Args:
            ip_address (str): The IP address to lookup.

        Returns:
            dict: The JSON response from the IP API.

        Raises:
            ValueError: If the IP address is not provided.
        """
        if not ip_address:
            raise ValueError("IP address is required to fetch information.")

        try:
            # Construct the URL with query parameters
            params = {"ip": ip_address, "api_key": self.api_key}
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred while fetching IP information: {response.json()}")
            return None
