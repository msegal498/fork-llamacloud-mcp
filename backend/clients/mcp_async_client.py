"""
Asynchronous MCP client that uses the async interface properly
"""
from dotenv import load_dotenv
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
import asyncio
import os
import logging
import argparse
import sys
sys.path.append("../../")  # Add the project root to path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path="../../config/.env")

async def run_agent(query: str):
    try:
        # Get MCP server URL from environment variable
        mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        logger.info(f"Connecting to MCP server at {mcp_server_url}")
        
        # Initialize MCP client
        mcp_client = BasicMCPClient(mcp_server_url)
        mcp_tool_spec = McpToolSpec(
            client=mcp_client,
        )

        # Get tools from MCP server asynchronously
        try:
            logger.info("Fetching tools from MCP server asynchronously...")
            tools = await mcp_tool_spec.to_tool_list_async()
            
            if not tools:
                logger.warning("No tools found from MCP server")
                print("Warning: No tools were found from the MCP server.")
                return
                
            logger.info(f"Successfully retrieved {len(tools)} tools from MCP server")
            for tool in tools:
                logger.info(f"Tool available: {tool.metadata.name}")
                
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
            logger.info("OpenAI LLM initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {str(e)}")
            print(f"Error initializing OpenAI: {str(e)}")
            return

        # Create agent
        agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt="You are an agent that knows how to build agents in LlamaIndex. Answer questions about LlamaIndex documentation accurately and concisely.",
            verbose=True
        )
        
        # Run agent
        logger.info(f"Running agent with query: {query}")
        print(f"\nProcessing query: {query}\n")
        print("=" * 50)
        
        # Check if agent.run is a coroutine function
        if asyncio.iscoroutinefunction(agent.run):
            response = await agent.run(query)
        else:
            # Use asyncio.to_thread to run synchronous function in a separate thread
            response = await asyncio.to_thread(agent.run, query)
            
        print("=" * 50)
        print("\nResponse:")
        print(response)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run LlamaIndex MCP client with async support')
    parser.add_argument('query', nargs='?', default="What is LlamaIndex?", 
                        help='Query to send to the agent (default: "What is LlamaIndex?")')
    args = parser.parse_args()
    
    # Run the agent with the provided query
    asyncio.run(run_agent(args.query))

if __name__ == "__main__":
    main()
