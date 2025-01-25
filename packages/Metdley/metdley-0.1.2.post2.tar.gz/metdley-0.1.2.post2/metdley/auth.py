from typing import Optional
from .client import Metdley

_client: Optional[Metdley] = None


def get_client() -> Metdley:
    """
    Retrieve the global Metdley client instance.

    Returns:
        Metdley: The authenticated Metdley client instance.

    Raises:
        RuntimeError: If the client is not initialized (i.e., auth() has not been called).
    """
    if _client is None:
        raise RuntimeError("Call auth() before making API calls.")
    return _client


def auth(api_key: str) -> None:
    """
    Authenticate with the API using the provided API key.

    Args:
        api_key (str): The API key for authentication.

    Note:
        It's strongly recommended to store your API key as an environment variable.

    Raises:
        ValueError: If the API key is invalid or authentication fails.
    """
    global _client
    _client = Metdley(api_key)
