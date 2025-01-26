import pytest
import os

def setup_environment():
    """Set up environment variables if not already set."""
    # if not os.getenv("UNSTRUCTURED_API_KEY"):
        # You can set your API key here for testing
        # os.environ["UNSTRUCTURED_API_KEY"] = "Gyf6wTNjlh2gP41whS5mPzL107sNqO"

def run_specific_test(test_name=None):
    """Run a specific test or all tests."""
    test_path = "./tests/test_integration.py"
    
    if test_name:
        # Run specific test with full traceback
        pytest.main([test_path, "-v", "-s", "--tb=long", "-k", test_name])
    else:
        # Run all tests with full traceback
        pytest.main([test_path, "-v", "-s", "--tb=long"])

if __name__ == "__main__":
    setup_environment()
    
    # Example: Run specific tests
    # Uncomment the test you want to run
    
    # run_specific_test("test_source_connector_lifecycle")
    # run_specific_test("test_destination_connector_lifecycle")
    # run_specific_test("test_workflow_lifecycle")
    
    # Or run all tests
    run_specific_test() 