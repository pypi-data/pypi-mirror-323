"""Integration tests for the Unstructured Platform SDK.

These tests make real API calls and require valid credentials.
To run these tests, you need to set the following environment variables:
- UNSTRUCTURED_API_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
"""

import os
import pytest
from datetime import datetime

from unstructured_platform import UnstructuredPlatformClient
from unstructured_platform.models import (
    PublicSourceConnectorType,
    PublicDestinationConnectorType,
    WorkflowAutoStrategy,
    WorkflowSchedule,
    CronTabEntry,
)


@pytest.fixture
def required_env_vars():
    """Check for required environment variables."""
    required_vars = ["UNSTRUCTURED_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(f"Missing required environment variables: {', '.join(missing)}")

@pytest.fixture
def client(required_env_vars):
    """Create a real API client."""
    return UnstructuredPlatformClient(api_key=os.getenv("UNSTRUCTURED_API_KEY"))


def test_source_connector_lifecycle(client):
    """Test the complete lifecycle of a source connector."""
    try:
        # Create
        source = client.sources.create(
            name=f"test-s3-source-{datetime.now().isoformat()}",
            type=PublicSourceConnectorType.S3,
            config={
                "remote_url": "s3://unstructured-testing/input",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            }
        )
        assert source.name.startswith("test-s3-source-")
        
        # Get
        retrieved = client.sources.get(source_id=source.id)
        assert retrieved.id == source.id
        assert retrieved.name == source.name
        
        # List
        sources = client.sources.list()
        assert any(s.id == source.id for s in sources)
        
        # Update
        updated = client.sources.update(
            source_id=source.id,
            config={
                "remote_url": "s3://unstructured-testing/input-updated",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            }
        )
        assert updated.id == source.id
        assert "input-updated" in updated.config["remote_url"]
        
        # Delete
        client.sources.delete(source_id=source.id)
        
        # Verify deletion - capture and check the exception
        with pytest.raises(Exception) as excinfo:
            client.sources.get(source_id=source.id)
        # print(f"Expected exception occurred: {excinfo.value}")
    except Exception as e:
        print("\n\nResponse: ", e.response.text)
        print(f"\nFull exception details:")
        import traceback
        print(traceback.format_exc())
        raise  # Re-raise the exception after printing details


def test_destination_connector_lifecycle(client):
    """Test the complete lifecycle of a destination connector."""
    
    try:
        # Create
        destination = client.destinations.create(
            name=f"test-es-destination-{datetime.now().isoformat()}",
            type=PublicDestinationConnectorType.S3,
            config={
                "remote_url": "s3://unstructured-testing/output",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            }
        )
        assert destination.name.startswith("test-es-destination-")
        
        # Get
        retrieved = client.destinations.get(destination_id=destination.id)
        assert retrieved.id == destination.id
        assert retrieved.name == destination.name
        
        # List
        destinations = client.destinations.list()
        assert any(d.id == destination.id for d in destinations)
        
        # Update
        updated = client.destinations.update(
            destination_id=destination.id,
            config={
                "remote_url": "s3://unstructured-testing/input-updated",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            }
        )
        assert updated.id == destination.id
        assert "input-updated" in updated.config["remote_url"]
        
        # Delete
        client.destinations.delete(destination_id=destination.id)
        
        # Verify deletion - capture and check the exception
        with pytest.raises(Exception) as excinfo:
            client.destinations.get(destination_id=destination.id)
        # print(f"Expected exception occurred: {excinfo.value}")
        
    except Exception as e:
        print("\n\nResponse: ", e.response.text)
        print(f"\nFull exception details:")
        import traceback
        print(traceback.format_exc())
        raise 

def test_workflow_lifecycle(client):
    """Test the complete lifecycle of a workflow."""
    
    try:
        # Create source and destination first
        source = client.sources.create(
            name=f"test-s3-source-{datetime.now().isoformat()}",
            type=PublicSourceConnectorType.S3,
            config={
                "remote_url": "s3://unstructured-testing/input",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            },
        )
    
        destination = client.destinations.create(
            name=f"test-es-destination-{datetime.now().isoformat()}",
            type=PublicDestinationConnectorType.S3,
            config={
                "remote_url": "s3://unstructured-testing/output",
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY")
            },
        )
        
        # Create workflow
        workflow = client.workflows.create(
            name=f"test-workflow-{datetime.now().isoformat()}",
            source_id=source.id,
            destination_id=destination.id,
            workflow_type=WorkflowAutoStrategy.BASIC,
            schedule="",       # "0 0 * * *" - Every day at midnight
        )
        assert workflow.name.startswith("test-workflow-")
        
        # Get
        retrieved = client.workflows.get(workflow_id=workflow.id)
        assert retrieved.id == workflow.id
        assert retrieved.name == workflow.name
        
        # List
        workflows = client.workflows.list()
        assert any(w.id == workflow.id for w in workflows)
        
        # Update
        updated = client.workflows.update(
            workflow_id=workflow.id,
            name=f"updated-{workflow.name}",
        )
        assert updated.id == workflow.id
        assert updated.name.startswith("updated-")
        
        # Run - To not incur costs, we will not run the job in this test
        # run_result = client.workflows.run(workflow_id=workflow.id)
        #assert run_result.id == workflow.id
        
        # Get job status
        jobs = client.jobs.list()
        assert len(jobs) > 0
        
        # Delete workflow
        client.workflows.delete(workflow_id=workflow.id)
        
        # Verify deletion - capture and check the exception
        with pytest.raises(Exception) as excinfo:
            client.workflows.get(workflow_id=workflow.id)
        print(f"Expected exception occurred: {excinfo.value}")
    except Exception as e:
        # print("\n\nResponse: ", e.response.text)
        print(f"\nFull exception details:")
        import traceback
        print(traceback.format_exc())
        raise 
            
    finally:
        # Cleanup
        client.sources.delete(source_id=source.id)
        client.destinations.delete(destination_id=destination.id) 