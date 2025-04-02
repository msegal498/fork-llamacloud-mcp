from dotenv import load_dotenv
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
import asyncio
import os
import logging
import argparse
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def run_agent(query: str):
    try:
        # Get MCP server URL from environment variable
        mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        logger.info(f"Connecting to MCP server at {mcp_server_url}")
        
        # Initialize MCP client
        mcp_client = BasicMCPClient(mcp_server_url)
        mcp_tool_spec = McpToolSpec(
            client=mcp_client,
            # Optional: Filter the tools by name
            # allowed_tools=["tool1", "tool2"],
        )

        # Get tools from MCP server
        try:
            tools = mcp_tool_spec.to_tool_list()
            if not tools:
                logger.warning("No tools found from MCP server")
        except Exception as e:
            logger.error(f"Failed to get tools from MCP server: {str(e)}")
            print(f"Error: Could not connect to MCP server. Is it running at {mcp_server_url}?")
            return
        
        # Initialize OpenAI LLM
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.error("OpenAI API key not found in environment variables")
                print("Error: OpenAI API key not found. Please add it to your .env file.")
                return
                
            llm = OpenAI(model="gpt-4o-mini")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
            print(f"Error initializing OpenAI: {str(e)}")
            return

        # Create and run agent
        agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt="You are an agent that knows how to build agents in LlamaIndex.",
        )
        
        logger.info(f"Running agent with query: {query}")
        response = await agent.run(query)
        print(response)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run LlamaIndex MCP client')
    parser.add_argument('query', nargs='?', default=" ", 
                        help='Query to send to the agent')
    args = parser.parse_args()
    
    # Run the agent with the provided query
    asyncio.run(run_agent(args.query))

if __name__ == "__main__":
    main()
