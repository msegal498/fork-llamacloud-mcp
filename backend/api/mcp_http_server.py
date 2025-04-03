"""
HTTP Server implementation for the PDF chunking system.
This module provides a FastAPI-based HTTP server for PDF processing.
"""

import os
import asyncio
import logging
import uuid
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add parent directory to path to allow importing from sibling packages
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Set current working directory to project root for consistent path resolution
project_root = parent_dir.parent
os.chdir(project_root)

# Import the shared client
from backend.clients.shared_llama_client import SharedLlamaClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables - use absolute path
config_path = Path(__file__).resolve().parent.parent.parent / "config" / ".env"
load_dotenv(dotenv_path=str(config_path))

# Get config from environment variables
port = int(os.getenv("MCP_SERVER_PORT", "8000"))
server_name = os.getenv("MCP_SERVER_NAME", "pdf-chunking-server")
upload_dir = os.getenv("PDF_UPLOAD_DIR", "./data/uploads")
output_dir = os.getenv("PDF_OUTPUT_DIR", "./data/outputs")

# Ensure directories exist
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Initialize shared client for PDF processing
llama_client = SharedLlamaClient()

# Dictionary to store processing job information
processing_jobs = {}

# Create FastAPI app directly - no more FastMCP wrapper
app = FastAPI(
    title=server_name,
    description="PDF Chunking System API Server",
    version="1.0.0"
)

# LLM Tools registry to replace @mcp.tool() decorator
class LLMTools:
    """Registry for LLM-callable functions."""
    
    @staticmethod
    def llama_index_documentation(query: str) -> str:
        """Search the llama-index documentation for the given query."""
        try:
            logger.info(f"Documentation query received: {query}")
            result = llama_client.query_documentation(query)
            return result
        except Exception as e:
            error_msg = f"Error in llama_index_documentation tool: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

# API endpoint for the LLM documentation tool
@app.get("/api/llama-docs")
async def get_llama_docs(query: str):
    """API endpoint for querying llama documentation."""
    result = LLMTools.llama_index_documentation(query)
    return {"result": result}

# Add root endpoint for basic info
@app.get("/")
async def root_endpoint():
    """Root endpoint to provide basic information."""
    return {
        "name": "PDF Chunking System - API Server",
        "version": "1.0.0",
        "endpoints": {
            "/api/llama-docs": "Query llama-index documentation",
            "/pdf/upload": "Upload a PDF file for processing",
            "/pdf/status/{job_id}": "Check the status of a processing job",
            "/pdf/download/{job_id}": "Download a processed PDF",
            "/status": "Get the system status",
            "/test": "Test if the server is running properly"
        }
    }

# Add a simple test endpoint
@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify the server is running."""
    return {"status": "API Server is running properly", "server": server_name}

# PDF processing background task - unchanged
async def process_pdf_task(job_id: str, file_path: str):
    """Background task to process a PDF file."""
    try:
        logger.info(f"Starting PDF processing job {job_id} for file: {file_path}")
        # Update job status to processing
        processing_jobs[job_id]["status"] = "processing"
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                # Just read a bit to verify it's accessible
                f.read(1024)
        except Exception as file_error:
            raise RuntimeError(f"Cannot read PDF file: {str(file_error)}")
        
        # Process the PDF with more detailed error handling
        try:
            # Extract text
            extracted_text = llama_client.extract_text_from_pdf(file_path)
            processing_jobs[job_id]["status"] = "text_extracted"
            
            # Chunk the text
            chunks = llama_client.chunk_text(extracted_text)
            processing_jobs[job_id]["status"] = "text_chunked"
            
            # Summarize each chunk
            summaries = []
            for i, chunk in enumerate(chunks):
                try:
                    summary = llama_client.summarize_text(chunk)
                    summaries.append(summary)
                    processing_jobs[job_id]["progress"] = f"Summarized chunk {i+1}/{len(chunks)}"
                except Exception as sum_error:
                    logger.warning(f"Error summarizing chunk {i+1}: {str(sum_error)}")
                    # Use a fallback for failed summaries
                    summaries.append(chunk[:500] + "...(truncated)")
            
            # Create a combined summary
            combined_summary = "\n\n".join(summaries)
            processing_jobs[job_id]["status"] = "summarized"
            
            # Generate summary PDF
            summary_pdf_path = os.path.join(output_dir, f"{job_id}_summary.pdf")
            llama_client.generate_pdf(combined_summary, summary_pdf_path)
            
            # Update job status to complete
            result = {
                "input_pdf": file_path,
                "extracted_text_length": len(extracted_text),
                "num_chunks": len(chunks),
                "summary_length": len(combined_summary),
                "output_pdf": summary_pdf_path
            }
            
            processing_jobs[job_id].update({
                "status": "complete",
                "result": result,
                "output_pdf": summary_pdf_path
            })
            
            logger.info(f"Completed PDF processing job {job_id}")
            
        except Exception as process_error:
            raise RuntimeError(f"PDF processing failed: {str(process_error)}")
        
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        logger.error(error_msg)
        processing_jobs[job_id].update({
            "status": "error",
            "error": error_msg
        })

# Add PDF upload endpoint - unchanged
@app.post("/pdf/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a PDF file for processing."""
    try:
        # Validate file is a PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Create file path in upload directory
        file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store job information
        processing_jobs[job_id] = {
            "job_id": job_id,
            "status": "uploaded",
            "file_path": file_path,
            "original_filename": file.filename
        }
        
        # Start processing in background
        background_tasks.add_task(process_pdf_task, job_id, file_path)
        
        return {
            "job_id": job_id,
            "status": "uploaded",
            "message": "PDF uploaded and processing started"
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error uploading PDF: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Add PDF processing status endpoint - unchanged 
@app.get("/pdf/status/{job_id}")
async def get_pdf_status(job_id: str):
    """Get the status of a PDF processing job."""
    try:
        # Check if job exists
        if job_id not in processing_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Return job status
        return processing_jobs[job_id]
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error getting job status: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Add PDF download endpoint - unchanged
@app.get("/pdf/download/{job_id}")
async def download_pdf(job_id: str):
    """Download a processed PDF file."""
    try:
        # Check if job exists
        if job_id not in processing_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_info = processing_jobs[job_id]
        
        # Check if processing is complete
        if job_info["status"] != "complete":
            raise HTTPException(status_code=400, detail=f"PDF processing not complete. Current status: {job_info['status']}")
        
        # Check if output file exists
        output_pdf = job_info.get("output_pdf")
        if not output_pdf or not os.path.exists(output_pdf):
            raise HTTPException(status_code=404, detail="Processed PDF file not found")
        
        # Return the file
        return FileResponse(
            path=output_pdf,
            filename=f"processed_{Path(job_info['original_filename']).stem}.pdf",
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error downloading PDF: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Status endpoints - unchanged
@app.get("/api-status")
async def api_status():
    """Status endpoint specifically for API health checks."""
    return {
        "status": "running",
        "server": server_name,
        "port": port,
        "job_count": len(processing_jobs),
        "upload_dir": upload_dir,
        "output_dir": output_dir,
        "api_health": "ok"
    }

@app.get("/status")
async def get_system_status():
    """Get the status of the PDF processing system."""
    try:
        # Count jobs by status
        status_counts = {}
        for job in processing_jobs.values():
            status = job.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "status": "running",
            "jobs": {
                "total": len(processing_jobs),
                "by_status": status_counts
            },
            "directories": {
                "upload_dir": upload_dir,
                "output_dir": output_dir
            }
        }
    except Exception as e:
        error_msg = f"Error getting system status: {str(e)}"
        logger.error(error_msg)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": error_msg}
        )

# Simple, direct server startup - no more complex MCP startup logic
def main():
    """Start the API server."""
    import uvicorn
    logger.info(f"Starting API server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()