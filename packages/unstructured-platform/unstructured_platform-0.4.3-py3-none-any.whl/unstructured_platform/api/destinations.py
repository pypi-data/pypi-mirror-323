"""Destinations API resource."""

from typing import List, Optional, Dict, Any
from pydantic import UUID4

from unstructured_platform.api.base import BaseAPI
from unstructured_platform.models import (
    DestinationConnector,
    PublicDestinationConnectorType,
)


class DestinationsAPI(BaseAPI):
    """Destinations API resource."""

    def list(
        self,
        destination_type: Optional[PublicDestinationConnectorType] = None,
    ) -> List[DestinationConnector]:
        """List destination connectors.

        Args:
            destination_type: Filter by destination connector type

        Returns:
            List of destination connectors
        """
        params = {"destination_type": destination_type.value if destination_type else None}
        data = self.client.request("GET", "destinations", params=params)
        return [DestinationConnector.model_validate(item) for item in data]

    def create(
        self,
        name: str,
        type: PublicDestinationConnectorType,
        config: Dict[str, Any],
    ) -> DestinationConnector:
        """Create a destination connector.

        Args:
            name: Name of the connector
            type: Type of the connector
            config: Connector configuration

        Returns:
            Created destination connector
        """
        data = self.client.request(
            "POST",
            "destinations",
            json={
                "name": name,
                "type": type.value,
                "config": config,
            },
        )
        # Preserve original values while keeping any additional config keys added by API (if any)
        data["config"] = {**data["config"], **config}
        
        return DestinationConnector.model_validate(data)

    def get(self, destination_id: UUID4) -> DestinationConnector:
        """Get a destination connector.

        Args:
            destination_id: ID of the destination connector

        Returns:
            Destination connector
        """
        data = self.client.request("GET", f"destinations/{destination_id}")
        return DestinationConnector.model_validate(data)

    def update(
        self,
        destination_id: UUID4,
        config: Dict[str, Any],
    ) -> DestinationConnector:
        """Update a destination connector.

        Args:
            destination_id: ID of the destination connector
            config: New connector configuration

        Returns:
            Updated destination connector
        """
        data = self.client.request(
            "PUT",
            f"destinations/{destination_id}",
            json={"config": config},
        )
        # Preserve original values while keeping any additional config keys added by API (if any)
        data["config"] = {**data["config"], **config}
        
        return DestinationConnector.model_validate(data)

    def delete(self, destination_id: UUID4) -> None:
        """Delete a destination connector.

        Args:
            destination_id: ID of the destination connector
        """
        self.client.request("DELETE", f"destinations/{destination_id}") 