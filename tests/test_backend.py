"""
Unit tests for the backend components
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMCPServer(unittest.TestCase):
    """Tests for the MCP server implementation"""
    
    @patch('backend.llamacloud_mcp.mcp_server.LlamaCloudIndex')
    def test_llama_index_documentation(self, mock_index):
        """Test the llama_index_documentation tool function"""
        from backend.llamacloud_mcp.mcp_server import llama_index_documentation
        
        # Mock the environment variables
        with patch.dict(os.environ, {
            "LLAMA_CLOUD_INDEX_NAME": "test-index",
            "LLAMA_CLOUD_PROJECT_NAME": "test-project",
            "LLAMA_CLOUD_ORG_ID": "test-org-id",
            "LLAMA_CLOUD_API_KEY": "test-api-key"
        }):
            # Mock the query engine response
            mock_query_engine = MagicMock()
            mock_query_engine.query.return_value = "Test response"
            
            mock_index_instance = MagicMock()
            mock_index_instance.as_query_engine.return_value = mock_query_engine
            mock_index.return_value = mock_index_instance
            
            # Call the function
            result = llama_index_documentation("test query")
            
            # Check the result
            self.assertEqual(result, "Test response")
            
            # Check that the index was initialized with correct parameters
            mock_index.assert_called_once_with(
                name="test-index",
                project_name="test-project",
                organization_id="test-org-id",
                api_key="test-api-key"
            )
            
            # Check that the query was called
            mock_query_engine.query.assert_called_once_with("test query")
    
    @patch('backend.llamacloud_mcp.mcp_server.LlamaCloudIndex')
    def test_llama_index_documentation_missing_env_vars(self, mock_index):
        """Test the llama_index_documentation tool function with missing environment variables"""
        from backend.llamacloud_mcp.mcp_server import llama_index_documentation
        
        # Mock the environment variables to be empty
        with patch.dict(os.environ, {}, clear=True):
            # Call the function
            result = llama_index_documentation("test query")
            
            # Check the result contains error message
            self.assertTrue("Error: Missing required LlamaCloud configuration" in result)
            
            # Check that the index was not initialized
            mock_index.assert_not_called()

if __name__ == '__main__':
    unittest.main()
