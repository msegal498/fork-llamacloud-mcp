"""
Remote MCP client implementation for the PDF chunking system.
This module provides a client for remote HTTP interaction with the MCP server.
"""

from dotenv import load_dotenv
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
import asyncio
import os
import logging
import argparse
import httpx
import json
import tempfile
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClientRemote:
    """
    MCP client for remote HTTP interaction with the MCP server.
    
    This client is designed for web-based interactions with the MCP HTTP server.
    """
    
    def __init__(self, server_url: Optional[str] = None, env_path: Optional[str] = None):
        """
        Initialize the remote MCP client.
        
        Args:
            server_url: URL of the MCP HTTP server (default: from env)
            env_path: Optional path to .env file for configuration
        """
        # Load environment variables
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()
        
        # Get MCP server URL
        self.server_url = server_url or os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        logger.info(f"Remote MCP client initialized with server URL: {self.server_url}")
        
        # Initialize HTTP client for API calls
        self._http_client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for PDF processing
    
    async def close(self):
        """Close the HTTP client when done."""
        await self._http_client.aclose()
    
    async def query_documentation(self, query: str) -> Dict[str, Any]:
        """
        Query the LlamaCloud documentation via the MCP server.
        
        Args:
            query: The query string
            
        Returns:
            Response dictionary
        """
        try:
            logger.info(f"Sending documentation query to MCP server: {query}")
            response = await self._http_client.post(
                f"{self.server_url}/tools/llama_index_documentation",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_msg = f"Error querying documentation: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    async def upload_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a PDF file to the MCP server.
        
        Args:
            file_path: Path to the PDF file to upload
            
        Returns:
            Response dictionary with job ID
        """
        try:
            logger.info(f"Uploading PDF to MCP server: {file_path}")
            
            # Verify file exists
            if not os.path.exists(file_path):
                error_msg = f"PDF file not found: {file_path}"
                logger.error(error_msg)
                return {"status": "error", "error": error_msg}
            
            # Create form data with file
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f, "application/pdf")}
                response = await self._http_client.post(
                    f"{self.server_url}/pdf/upload",
                    files=files
                )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            error_msg = f"Error uploading PDF: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    async def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a PDF processing job.
        
        Args:
            job_id: Processing job ID
            
        Returns:
            Status dictionary
        """
        try:
            logger.info(f"Getting processing status for job: {job_id}")
            response = await self._http_client.get(
                f"{self.server_url}/pdf/status/{job_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            error_msg = f"Error getting processing status: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    async def download_processed_pdf(self, job_id: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Download a processed PDF file.
        
        Args:
            job_id: Processing job ID
            output_path: Path where to save the downloaded file (optional)
            
        Returns:
            Dictionary with download info including the file path
        """
        try:
            logger.info(f"Downloading processed PDF for job: {job_id}")
            
            # Get the file
            response = await self._http_client.get(
                f"{self.server_url}/pdf/download/{job_id}",
                follow_redirects=True
            )
            response.raise_for_status()
            
            # Create output path if not provided
            if not output_path:
                # Create a temporary file with PDF extension
                fd, output_path = tempfile.mkstemp(suffix=".pdf")
                os.close(fd)
            
            # Save the response content to the output path
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Downloaded processed PDF to: {output_path}")
            return {
                "status": "success",
                "job_id": job_id,
                "file_path": output_path,
                "message": f"Downloaded processed PDF to: {output_path}"
            }
            
        except Exception as e:
            error_msg = f"Error downloading processed PDF: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

async def run_client_command(args):
    """Run a command with the remote MCP client."""
    client = MCPClientRemote()
    
    try:
        if args.command == "query":
            result = await client.query_documentation(args.query)
            print(json.dumps(result, indent=2))
            
        elif args.command == "upload":
            result = await client.upload_pdf(args.file_path)
            print(json.dumps(result, indent=2))
            
        elif args.command == "status":
            result = await client.get_processing_status(args.job_id)
            print(json.dumps(result, indent=2))
            
        elif args.command == "download":
            result = await client.download_processed_pdf(args.job_id, args.output_path)
            print(json.dumps(result, indent=2))
            
        else:
            print(f"Unknown command: {args.command}")
            
    finally:
        await client.close()

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run MCP remote client commands')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query documentation')
    query_parser.add_argument('query', help='Query string')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a PDF file')
    upload_parser.add_argument('file_path', help='Path to PDF file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get processing status')
    status_parser.add_argument('job_id', help='Job ID')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download processed PDF')
    download_parser.add_argument('job_id', help='Job ID')
    download_parser.add_argument('--output-path', help='Path to save the downloaded file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the client with the provided command
    asyncio.run(run_client_command(args))

if __name__ == "__main__":
    main()
