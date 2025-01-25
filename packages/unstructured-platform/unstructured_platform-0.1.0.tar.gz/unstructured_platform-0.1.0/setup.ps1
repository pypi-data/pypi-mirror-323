# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install the package in development mode with test dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest -v 