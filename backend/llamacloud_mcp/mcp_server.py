"""
MCP Server implementation for PDF chunking system in CLI mode.
This module provides a command-line interface for invoking LlamaCloud and OpenAI APIs
to process PDFs and query documentation.
"""

from dotenv import load_dotenv
import os
import logging
import json
import asyncio
import sys
from pathlib import Path
import argparse

# Set up project paths
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Set current working directory to project root for consistent path resolution
project_root = Path(__file__).resolve().parent.parent.parent
os.chdir(project_root)

# Import the local client for processing tasks
from backend.clients.mcp_client_local import MCPClientLocal

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
server_name = os.getenv("MCP_SERVER_NAME", "llama-index-server")

# Initialize local client
client = MCPClientLocal()

def llama_index_documentation(query: str) -> str:
    """Search the llama-index documentation for the given query."""
    try:
        logger.info(f"Documentation query received: {query}")
        result = asyncio.run(client.query_documentation(query))
        return result
    except Exception as e:
        error_msg = f"Error in llama_index_documentation tool: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

def process_pdf(file_path: str) -> str:
    """
    Process a PDF file: extract text, chunk, summarize, and generate a new PDF.
    
    Args:
        file_path: Path to the PDF file to process
    
    Returns:
        JSON string with processing results
    """
    try:
        logger.info(f"PDF processing request received for: {file_path}")
        result = asyncio.run(client.process_pdf(file_path))
        return json.dumps(result)
    except Exception as e:
        error_msg = f"Error in process_pdf tool: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"status": "error", "error": error_msg})

def get_processing_status(job_id: str) -> str:
    """
    Get the status of a PDF processing job.
    
    Args:
        job_id: Processing job ID
    
    Returns:
        JSON string with job status information
    """
    try:
        logger.info(f"Status request received for job: {job_id}")
        result = asyncio.run(client.get_processing_status(job_id))
        return json.dumps(result)
    except Exception as e:
        error_msg = f"Error in get_processing_status tool: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"status": "error", "error": error_msg})

def main():
    logger.info("Starting MCP server in command-line mode")
    
    parser = argparse.ArgumentParser(description="MCP Server Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for documentation query
    parser_doc = subparsers.add_parser("docs", help="Query llama-index documentation")
    parser_doc.add_argument("query", type=str, help="Query string for documentation")

    # Subparser for PDF processing
    parser_pdf = subparsers.add_parser("process", help="Process a PDF file")
    parser_pdf.add_argument("file_path", type=str, help="Path to the PDF file")

    # Subparser for checking processing status
    parser_status = subparsers.add_parser("status", help="Get processing status for a job")
    parser_status.add_argument("job_id", type=str, help="Job ID to check status")

    args = parser.parse_args()

    if args.command == "docs":
        output = llama_index_documentation(args.query)
        print(output)
    elif args.command == "process":
        output = process_pdf(args.file_path)
        print(output)
    elif args.command == "status":
        output = get_processing_status(args.job_id)
        print(output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
