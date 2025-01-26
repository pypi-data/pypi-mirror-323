"""Workflows API resource."""

from typing import List, Optional
from pydantic import UUID4

from unstructured_platform.api.base import BaseAPI
from unstructured_platform.models import (
    WorkflowInformation,
    WorkflowState,
    WorkflowAutoStrategy,
    WorkflowSchedule,
)


class WorkflowsAPI(BaseAPI):
    """Workflows API resource."""

    def list(
        self,
        source_id: Optional[UUID4] = None,
        destination_id: Optional[UUID4] = None,
        status: Optional[WorkflowState] = None,
    ) -> List[WorkflowInformation]:
        """List workflows.

        Args:
            source_id: Filter by source connector ID
            destination_id: Filter by destination connector ID
            status: Filter by workflow status

        Returns:
            List of workflows
        """
        params = {
            "source_id": str(source_id) if source_id else None,
            "destination_id": str(destination_id) if destination_id else None,
            "status": status.value if status else None,
        }
        data = self.client.request("GET", "workflows", params=params)
        return [WorkflowInformation.model_validate(item) for item in data]

    def create(
        self,
        name: str,
        source_id: UUID4,
        destination_id: UUID4,
        workflow_type: WorkflowAutoStrategy,
        schedule: str,
    ) -> WorkflowInformation:
        """Create a workflow.

        Args:
            name: Name of the workflow
            source_id: Source connector ID
            destination_id: Destination connector ID
            workflow_type: Type of workflow processing
            schedule: Cron expression string for workflow schedule

        Returns:
            Created workflow
        """
        data = self.client.request(
            "POST",
            "workflows",
            json={
                "name": name,
                "source_id": str(source_id),
                "destination_id": str(destination_id),
                "workflow_type": workflow_type.value,
                "schedule": schedule,
            },
        )
        
        return WorkflowInformation.model_validate(data)

    def get(self, workflow_id: UUID4) -> WorkflowInformation:
        """Get a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Workflow information
        """
        data = self.client.request("GET", f"workflows/{workflow_id}")
        return WorkflowInformation.model_validate(data)

    def update(
        self,
        workflow_id: UUID4,
        name: Optional[str] = None,
        source_id: Optional[UUID4] = None,
        destination_id: Optional[UUID4] = None,
        workflow_type: Optional[WorkflowAutoStrategy] = None,
        schedule: Optional[str] = None,  # Changed from WorkflowSchedule to str
    ) -> WorkflowInformation:
        """Update a workflow.

        Args:
            workflow_id: ID of the workflow
            name: New name for the workflow
            source_id: New source connector ID
            destination_id: New destination connector ID
            workflow_type: New workflow processing type
            schedule: New workflow schedule as cron expression string

        Returns:
            Updated workflow
        """
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if source_id is not None:
            update_data["source_id"] = str(source_id)
        if destination_id is not None:
            update_data["destination_id"] = str(destination_id)
        if workflow_type is not None:
            update_data["workflow_type"] = workflow_type.value
        if schedule is not None:
            update_data["schedule"] = schedule  # No longer needs model_dump()

        data = self.client.request(
            "PUT",
            f"workflows/{workflow_id}",
            json=update_data,
        )
        return WorkflowInformation.model_validate(data)

    def delete(self, workflow_id: UUID4) -> None:
        """Delete a workflow.

        Args:
            workflow_id: ID of the workflow
        """
        self.client.request("DELETE", f"workflows/{workflow_id}")

    def run(self, workflow_id: UUID4) -> WorkflowInformation:
        """Run a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Updated workflow information
        """
        data = self.client.request("POST", f"workflows/{workflow_id}/run")
        return WorkflowInformation.model_validate(data)
    
    