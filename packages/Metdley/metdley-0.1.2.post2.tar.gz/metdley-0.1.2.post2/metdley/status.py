from dataclasses import dataclass
from datetime import datetime

from .auth import get_client


@dataclass
class StatusResponse:
    """Data class representing the API status response."""

    status: str
    version: str
    request_time: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StatusResponse":
        """Create a StatusResponse instance from a dictionary."""
        return cls(
            status=data["status"],
            version=data["version"],
            request_time=datetime.fromisoformat(data["request_time"]),
        )


class Status:
    def check(self) -> StatusResponse:
        """
        Check the current status of the Metdley API.

        Returns:
            StatusResponse: Object containing status information including:
                - status: Current operational status
                - version: API version
                - request_time: Timestamp of the status check
        """
        client = get_client()
        response = client.request("GET", "/status")
        return StatusResponse.from_dict(response)

    def is_operational(self) -> bool:
        """
        Check if the API is operational.

        Returns:
            bool: True if the API status is "Operational", False otherwise
        """
        return self.check().status == "Operational"


# Create instance
status = Status()
