"""Jobs API resource."""

from typing import List, Optional
from pydantic import UUID4

from unstructured_platform.api.base import BaseAPI
from unstructured_platform.models import JobInformation


class JobsAPI(BaseAPI):
    """Jobs API resource."""

    def list(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[JobInformation]:
        """List jobs.

        Args:
            workflow_id: Filter by workflow ID
            status: Filter by job status

        Returns:
            List of jobs
        """
        params = {
            "workflow_id": workflow_id,
            "status": status,
        }
        data = self.client.request("GET", "jobs", params=params)
        return [JobInformation.model_validate(item) for item in data]

    def get(self, job_id: UUID4) -> JobInformation:
        """Get a job.

        Args:
            job_id: ID of the job

        Returns:
            Job information
        """
        data = self.client.request("GET", f"jobs/{job_id}")
        return JobInformation.model_validate(data)

    def cancel(self, job_id: UUID4) -> None:
        """Cancel a job.

        Args:
            job_id: ID of the job
        """
        self.client.request("POST", f"jobs/{job_id}/cancel") 