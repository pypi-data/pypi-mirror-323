"""Base class for API resources."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unstructured_platform.client import UnstructuredPlatformClient


class BaseAPI:
    """Base class for API resources."""

    def __init__(self, client: "UnstructuredPlatformClient"):
        """Initialize the API resource.

        Args:
            client: The Unstructured Platform client instance
        """
        self.client = client 