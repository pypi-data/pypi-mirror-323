# Integration Tests

These tests make real API calls to the Unstructured Platform API and verify the complete functionality of the SDK.

## Setup

1. Set your API key as an environment variable:
   ```bash
   # Unix/Linux/MacOS
   export UNSTRUCTURED_API_KEY="your-api-key"
   
   # Windows (Command Prompt)
   set UNSTRUCTURED_API_KEY=your-api-key
   
   # Windows (PowerShell)
   $env:UNSTRUCTURED_API_KEY = "your-api-key"
   ```

2. Install test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Running Tests

Run all integration tests:
```bash
pytest tests -v
```

Run a specific test:
```bash
pytest tests/test_integration.py::test_source_connector_lifecycle -v
pytest tests/test_integration.py::test_destination_connector_lifecycle -v
pytest tests/test_integration.py::test_workflow_lifecycle -v
```

## What's Being Tested

The integration tests verify:

1. **Source Connectors**
   - Creation with real configurations
   - Retrieval of created connectors
   - Listing and filtering
   - Updates with new configurations
   - Deletion and cleanup

2. **Destination Connectors**
   - Creation with real configurations
   - Retrieval of created connectors
   - Listing and filtering
   - Updates with new configurations
   - Deletion and cleanup

3. **Workflows**
   - Creation with real source and destination
   - Retrieval of created workflows
   - Listing and filtering
   - Updates to workflow configuration
   - Running workflows
   - Job status monitoring
   - Deletion and cleanup

4. **Error Handling**
   - Verification of proper error responses
   - Cleanup of test resources even if tests fail

## Test Data

The tests create resources with unique names using timestamps to avoid conflicts:
- `test-s3-source-{timestamp}`
- `test-es-destination-{timestamp}`
- `test-workflow-{timestamp}`

All test resources are cleaned up after the tests complete, even if tests fail. 