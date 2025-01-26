# Unstructured Platform SDK

<p align="center">
  <img src="https://raw.githubusercontent.com/Unstructured-IO/unstructured/main/img/unstructured_logo.png" alt="Unstructured.io Logo" width="150"/>
</p>

A Python SDK for the [Unstructured Platform API](https://docs.unstructured.io/platform/api/overview).

Unstructured Platform is an enterprise-grade ETL (Extract, Transform, Load) platform designed specifically for Large Language Models (LLMs). It provides a no-code UI and production-ready infrastructure to help organizations transform raw, unstructured data into LLM-ready formats. With over 18 million downloads and used by more than 50,000 companies, Unstructured Platform enables data scientists and engineers to spend less time collecting and cleaning data, and more time on modeling and analysis.

This SDK was developed by [One Minute AI](https://www.oneminuteai.com) to make it easier for Python developers to interact with the Unstructured Platform API. One Minute AI allows you to **transform your data** into **custom AI assistants and apps** in seconds, powered by Unstructured's enterprise data engine.

<!-- Hidden
<div align="right">
  <img src="https://cdn.prod.website-files.com/66ea86f2d3f578eb9978c2c4/66ea8cd694fdca03dcd51d54_OneMinuteLogo%202.svg" alt="One Minute AI Logo" width="100"/>
</div>
-->

- [Unstructured Platform SDK](#unstructured-platform-sdk)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Initialize the client](#initialize-the-client)
    - [Working with Source Connectors](#working-with-source-connectors)
    - [Working with Destination Connectors](#working-with-destination-connectors)
    - [Working with Workflows](#working-with-workflows)
    - [Working with Jobs](#working-with-jobs)

## Installation

```bash
pip install unstructured-platform
```

## Usage

### Initialize the client

```python
from unstructured_platform import UnstructuredPlatformClient

client = UnstructuredPlatformClient(api_key="your-api-key")
```

### Working with Source Connectors

```python
from unstructured_platform.models import PublicSourceConnectorType

# List source connectors
sources = client.sources.list()

# Create a source connector
source = client.sources.create(
    name="My S3 Source",
    type=PublicSourceConnectorType.S3,
    config={
        "remote_url": "s3://my-bucket/documents/",
        "key": "your-access-key",
        "secret": "your-secret-key",
    },
)

# Get a source connector
source = client.sources.get(source_id="source-id")

# Update a source connector
updated_source = client.sources.update(
    source_id="source-id",
    config={
        "remote_url": "s3://my-bucket/new-prefix/",
    },
)

# Delete a source connector
client.sources.delete(source_id="source-id")
```

### Working with Destination Connectors

```python
from unstructured_platform.models import PublicDestinationConnectorType

# List destination connectors
destinations = client.destinations.list()

# Create a destination connector
destination = client.destinations.create(
    name="My Pinecone Destination",
    type=PublicDestinationConnectorType.PINECONE,
    config={
        "environment": "us-west1-gcp",
        "api_key": "your-pinecone-api-key",
        "index_name": "documents",
        "namespace": "default",
    },
)

# Get a destination connector
destination = client.destinations.get(destination_id="destination-id")

# Update a destination connector
updated_destination = client.destinations.update(
    destination_id="destination-id",
    config={
        "namespace": "new-namespace",
    },
)

# Delete a destination connector
client.destinations.delete(destination_id="destination-id")
```

### Working with Workflows

```python
from unstructured_platform.models import WorkflowAutoStrategy

# List workflows
workflows = client.workflows.list()

# Create a workflow
workflow = client.workflows.create(
    name="My Daily Workflow",
    source_id="source-id",
    destination_id="destination-id",
    workflow_type=WorkflowAutoStrategy.BASIC,
    schedule="0 0 * * *",  # Daily at midnight
)

# Get a workflow
workflow = client.workflows.get(workflow_id="workflow-id")

# Update a workflow
updated_workflow = client.workflows.update(
    workflow_id="workflow-id",
    name="New Workflow Name",
)

# Delete a workflow
client.workflows.delete(workflow_id="workflow-id")

# Run a workflow
workflow = client.workflows.run(workflow_id="workflow-id")
```

### Working with Jobs

```python
# List jobs
jobs = client.jobs.list()

# Get a job
job = client.jobs.get(job_id="job-id")

# Cancel a job
client.jobs.cancel(job_id="job-id")
```