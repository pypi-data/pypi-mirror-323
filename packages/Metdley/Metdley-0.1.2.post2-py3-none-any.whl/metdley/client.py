import requests


class Metdley:
    """
    A client library for interacting with the Metdley API.

    The `Metdley` class provides a simple interface to send HTTP requests to the API.

    Attributes:
        api_key (str): The API key used for authenticating requests.
        base_url (str): The base URL for the API.
        headers (dict): Default headers included with every API request.
    """

    def __init__(self, api_key: str):
        """
        Initialize the Metdley client with an API key.

        Args:
            api_key (str): The API key used for authenticating requests.
        """
        self.api_key = api_key
        self.base_url = "http://api.metdley.com"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        body: bytes = None,
    ) -> dict:
        """
        Send an HTTP request to the API.

        This method constructs a full URL using the base URL and endpoint,
        and sends a request with the specified method, parameters, and data.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            endpoint (str): The endpoint to append to the base URL.
            params (dict, optional): Query parameters to include in the request. Defaults to None.
            data (dict, optional): JSON payload to include in the request body. Defaults to None.
            body (bytes, optional): Raw bytes to include in the request body. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails or the response status code is not 2xx.
        """
        url = f"{self.base_url}{endpoint}"  # Construct the full URL
        if body is not None:
            response = requests.request(
                method, url, headers=self.headers, params=params, data=body
            )
        else:
            response = requests.request(
                method, url, headers=self.headers, params=params, json=data
            )
        response.raise_for_status()  # Raise an error for HTTP responses with 4xx or 5xx status codes
        return response.json()  # Return the response JSON as a dictionary
