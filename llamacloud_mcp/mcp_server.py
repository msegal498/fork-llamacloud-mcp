from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get config from environment variables
server_name = os.getenv("MCP_SERVER_NAME", "llama-index-server")

# Initialize MCP server
mcp = FastMCP(server_name)

@mcp.tool()
def llama_index_documentation(query: str) -> str:
    """Search the llama-index documentation for the given query."""
    try:
        # Get LlamaCloud config from environment variables
        index_name = os.getenv("LLAMA_CLOUD_INDEX_NAME")
        project_name = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
        org_id = os.getenv("LLAMA_CLOUD_ORG_ID")
        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        
        # Validate required environment variables
        if not all([index_name, project_name, org_id, api_key]):
            error_msg = "Missing required LlamaCloud configuration. Check environment variables."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Initialize LlamaCloud index
        index = LlamaCloudIndex(
            name=index_name,
            project_name=project_name,
            organization_id=org_id,
            api_key=api_key,
        )
        
        logger.info(f"Querying LlamaCloud index: {index_name}")
        # Query the index (without the hardcoded enhancement)
        response = index.as_query_engine().query(query)
        
        return str(response)
        
    except Exception as e:
        error_msg = f"Error querying LlamaCloud: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

if __name__ == "__main__":
    logger.info(f"Starting MCP server with stdio transport")
    mcp.run(transport="stdio")
