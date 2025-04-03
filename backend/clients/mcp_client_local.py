"""
Local MCP client implementation for the PDF chunking system.
This module provides a client for local usage with stdio transport.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from .shared_llama_client import SharedLlamaClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClientLocal:
    """
    MCP client for local usage with stdio transport.
    
    This client is designed for development and testing with the local CLI.
    It uses the shared LlamaClient for PDF processing functionality.
    """
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize the local MCP client.
        
        Args:
            env_path: Optional path to .env file for configuration
        """
        self.llama_client = SharedLlamaClient(load_env_path=env_path)
        self.upload_dir = os.getenv("PDF_UPLOAD_DIR", "./data/uploads")
        self.output_dir = os.getenv("PDF_OUTPUT_DIR", "./data/outputs")
        
        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Local MCP client initialized with upload_dir={self.upload_dir}, output_dir={self.output_dir}")
    
    async def query_documentation(self, query: str) -> str:
        """
        Query the LlamaCloud documentation index.
        
        Args:
            query: The query string
            
        Returns:
            Response as a string
        """
        return self.llama_client.query_documentation(query)
    
    async def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file through the local client.
        
        Args:
            file_path: Path to the PDF file to process
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Verify file exists
            if not os.path.exists(file_path):
                error_msg = f"PDF file not found: {file_path}"
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Process the PDF
            result = self.llama_client.process_pdf(file_path, self.output_dir)
            
            return {
                "status": "success",
                "file_path": file_path,
                "result": result
            }
        except Exception as e:
            error_msg = f"Error processing PDF: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    async def get_processing_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a processing job.
        
        Args:
            job_id: Processing job ID
            
        Returns:
            Dictionary with job status information
        """
        # In the local version, we'll return a simple mock response
        # In a real implementation, this would check a database or file
        return {
            "status": "complete",
            "job_id": job_id,
            "message": "Processing complete"
        }
    
    async def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a command received from the MCP server.
        
        Args:
            command: Dictionary with command details
            
        Returns:
            Response dictionary
        """
        try:
            cmd_type = command.get("type")
            
            if cmd_type == "query_documentation":
                query = command.get("query", "")
                result = await self.query_documentation(query)
                return {"status": "success", "result": result}
                
            elif cmd_type == "process_pdf":
                file_path = command.get("file_path", "")
                result = await self.process_pdf(file_path)
                return result
                
            elif cmd_type == "get_status":
                job_id = command.get("job_id", "")
                result = await self.get_processing_status(job_id)
                return result
                
            else:
                return {"status": "error", "error": f"Unknown command type: {cmd_type}"}
                
        except Exception as e:
            error_msg = f"Error handling command: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
