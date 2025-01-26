"""Sources API resource."""

from typing import List, Optional, Dict, Any
from pydantic import UUID4

from unstructured_platform.api.base import BaseAPI
from unstructured_platform.models import (
    SourceConnector,
    PublicSourceConnectorType,
)


class SourcesAPI(BaseAPI):
    """Sources API resource."""

    def list(self, source_type: Optional[PublicSourceConnectorType] = None) -> List[SourceConnector]:
        """List source connectors.

        Args:
            source_type: Filter by source connector type

        Returns:
            List of source connectors
        """
        params = {"source_type": source_type.value if source_type else None}
        data = self.client.request("GET", "sources", params=params)
        return [SourceConnector.model_validate(item) for item in data]

    def create(
        self,
        name: str,
        type: PublicSourceConnectorType,
        config: Dict[str, Any],
    ) -> SourceConnector:
        """Create a source connector.

        Args:
            name: Name of the connector
            type: Type of the connector
            config: Connector configuration

        Returns:
            Created source connector
        """
        data = self.client.request(
            "POST",
            "sources",
            json={
                "name": name,
                "type": type.value,
                "config": config,
            },
        )
        
        # Preserve original values while keeping any additional config keys added by API (if any)
        data["config"] = {**data["config"], **config}
        
        return SourceConnector.model_validate(data)

    def get(self, source_id: UUID4) -> SourceConnector:
        """Get a source connector.

        Args:
            source_id: ID of the source connector

        Returns:
            Source connector
        """
        data = self.client.request("GET", f"sources/{source_id}")
        return SourceConnector.model_validate(data)

    def update(
        self,
        source_id: UUID4,
        config: Dict[str, Any],
    ) -> SourceConnector:
        """Update a source connector.

        Args:
            source_id: ID of the source connector
            config: New connector configuration

        Returns:
            Updated source connector
        """
        data = self.client.request(
            "PUT",
            f"sources/{source_id}",
            json={"config": config},
        )
        
        # Preserve original values while keeping any additional config keys added by API (if any)
        data["config"] = {**data["config"], **config}
        
        return SourceConnector.model_validate(data)

    def delete(self, source_id: UUID4) -> None:
        """Delete a source connector.

        Args:
            source_id: ID of the source connector
        """
        self.client.request("DELETE", f"sources/{source_id}") 