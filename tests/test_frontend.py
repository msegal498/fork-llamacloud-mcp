"""
Unit tests for the frontend components
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFrontendServer(unittest.TestCase):
    """Tests for the frontend server implementation"""
    
    def setUp(self):
        """Set up test environment"""
        # Use a patched environment to avoid loading real env vars
        self.env_patcher = patch.dict(os.environ, {
            "FRONTEND_PORT": "8080",
            "MCP_SERVER_URL": "http://localhost:8000",
            "LLAMA_CLOUD_INDEX_NAME": "test-index",
            "LLAMA_CLOUD_PROJECT_NAME": "test-project",
            "LLAMA_CLOUD_ORG_ID": "test-org-id",
            "LLAMA_CLOUD_API_KEY": "test-api-key"
        })
        self.env_patcher.start()
        
        # Now import the app after environment is patched
        from frontend.server.frontend_server import app
        self.client = TestClient(app)
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    def test_read_root(self):
        """Test the root endpoint returns HTML"""
        # Mock the file open operation
        with patch("builtins.open", MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=MagicMock(
                read=MagicMock(return_value="<html>Test HTML</html>")
            )),
            __exit__=MagicMock(return_value=None)
        ))):
            response = self.client.get("/")
            # Check status code is 200 OK
            self.assertEqual(response.status_code, 200)
            # Check content is HTML
            self.assertEqual(response.text, "<html>Test HTML</html>")
    
    @patch("frontend.server.frontend_server.LlamaCloudIndex")
    def test_handle_query_success(self, mock_index):
        """Test the query endpoint with successful response"""
        # Mock the query engine response
        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = "Test response"
        
        mock_index_instance = MagicMock()
        mock_index_instance.as_query_engine.return_value = mock_query_engine
        mock_index.return_value = mock_index_instance
        
        # Send a query
        response = self.client.post(
            "/query",
            json={"query": "test query"}
        )
        
        # Check status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check response contains the expected data
        self.assertEqual(response.json(), {"response": "Test response"})
        
        # Check that the query was made with the right parameters
        mock_index.assert_called_once_with(
            name="test-index", 
            project_name="test-project",
            organization_id="test-org-id",
            api_key="test-api-key"
        )
        mock_query_engine.query.assert_called_once_with("test query")
    
    @patch("frontend.server.frontend_server.LlamaCloudIndex")
    def test_handle_query_error(self, mock_index):
        """Test the query endpoint with error response"""
        # Make the query engine raise an exception
        mock_index.side_effect = Exception("Test error")
        
        # Send a query
        response = self.client.post(
            "/query",
            json={"query": "test query"}
        )
        
        # Check status code is 200 OK (error is handled in the response body)
        self.assertEqual(response.status_code, 200)
        # Check response contains the error message
        self.assertTrue("error" in response.json())
        self.assertTrue("Test error" in response.json()["error"])
    
    @patch("frontend.server.frontend_server.httpx.AsyncClient")
    async def test_check_status_success(self, mock_client):
        """Test the status endpoint with successful response"""
        # Mock the httpx client
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = mock_response
        mock_client.return_value = mock_instance
        
        # Get status
        response = self.client.get("/status")
        
        # Check status code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check response contains service statuses
        status_data = response.json()
        self.assertTrue("services" in status_data)
        self.assertTrue("environment" in status_data)
        self.assertTrue("mcp_server" in status_data["services"])
        self.assertTrue("llama_cloud" in status_data["services"])

if __name__ == '__main__':
    unittest.main()
