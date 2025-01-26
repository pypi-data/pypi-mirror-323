"""Main client for the Unstructured Platform API."""

import requests
from typing import Optional, Dict, Any

from unstructured_platform.api.sources import SourcesAPI
from unstructured_platform.api.destinations import DestinationsAPI
from unstructured_platform.api.workflows import WorkflowsAPI
from unstructured_platform.api.jobs import JobsAPI


class UnstructuredPlatformClient:
    """Client for interacting with the Unstructured Platform API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://platform.unstructuredapp.io/api/v1",
        timeout: int = 30,
    ):
        """Initialize the Unstructured Platform client.

        Args:
            api_key: Your Unstructured Platform API key
            base_url: The base URL for the API (defaults to production)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "unstructured-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        # Initialize API resources
        self.sources = SourcesAPI(self)
        self.destinations = DestinationsAPI(self)
        self.workflows = WorkflowsAPI(self)
        self.jobs = JobsAPI(self)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the Unstructured Platform API.

        Args:
            method: HTTP method
            path: API path (without base URL)
            params: Query parameters
            json: JSON body data

        Returns:
            API response data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json() if response.content else {} 