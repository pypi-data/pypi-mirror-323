#!/bin/bash

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # For Unix/macOS
# venv\Scripts\activate  # For Windows

# Install the package in development mode with test dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest -v 