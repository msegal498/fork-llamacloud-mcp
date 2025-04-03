"""
Frontend server for the PDF chunking system.
Provides a web interface and proxies requests to the MCP HTTP Server.
"""

import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
import os
import json
import logging
import httpx
import tempfile
import shutil
from typing import Optional
from dotenv import load_dotenv
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables - use absolute path
config_path = Path(__file__).resolve().parent.parent.parent / "config" / ".env"
load_dotenv(dotenv_path=str(config_path))

# Get config from environment variables
frontend_port = int(os.getenv("FRONTEND_PORT", "8080"))
mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# Initialize FastAPI app
app = FastAPI(title="PDF Chunking System Frontend")

# Mount static files directory - use absolute path
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Create HTTP client
http_client = httpx.AsyncClient(timeout=60.0)  # Extended timeout for PDF processing

# Add route for the root path
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    try:
        index_path = Path(__file__).parent.parent / "static" / "index.html"
        with open(index_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading application")

# Proxy route for PDF upload
@app.post("/pdf/upload")
async def proxy_pdf_upload(file: UploadFile = File(...)):
    """Proxy PDF upload requests to the MCP server."""
    try:
        logger.info(f"Proxying PDF upload: {file.filename}")
        
        # Create temporary file to store the upload
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            # Write uploaded file to temporary file
            with temp_file:
                shutil.copyfileobj(file.file, temp_file)
            
            # Create form data for proxied request
            with open(temp_file.name, "rb") as f:
                files = {"file": (file.filename, f, "application/pdf")}
                response = await http_client.post(
                    f"{mcp_server_url}/pdf/upload",
                    files=files
                )
            
            # Check response
            if response.status_code != 200:
                logger.error(f"MCP server returned error: {response.status_code} - {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": f"MCP server error: {response.text}"}
                )
            
            # Get the response data
            data = response.json()
            
            # Add original filename to the response
            data["original_filename"] = file.filename
            
            return data
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    except Exception as e:
        logger.error(f"Error proxying PDF upload: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload error: {str(e)}"}
        )

# Proxy route for checking PDF processing status
@app.get("/pdf/status/{job_id}")
async def proxy_pdf_status(job_id: str):
    """Proxy status check requests to the MCP server."""
    try:
        logger.info(f"Proxying status check for job: {job_id}")
        
        response = await http_client.get(f"{mcp_server_url}/pdf/status/{job_id}")
        
        if response.status_code != 200:
            logger.error(f"MCP server returned error: {response.status_code} - {response.text}")
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"MCP server error: {response.text}"}
            )
        
        return response.json()
        
    except Exception as e:
        logger.error(f"Error proxying status check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Status check error: {str(e)}"}
        )

# Proxy route for PDF download
@app.get("/pdf/download/{job_id}")
async def proxy_pdf_download(job_id: str):
    """Proxy PDF download requests to the MCP server."""
    try:
        logger.info(f"Proxying PDF download for job: {job_id}")
        
        response = await http_client.get(
            f"{mcp_server_url}/pdf/download/{job_id}",
            follow_redirects=True
        )
        
        if response.status_code != 200:
            logger.error(f"MCP server returned error: {response.status_code} - {response.text}")
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"MCP server error: {response.text}"}
            )
        
        # Get filename from Content-Disposition header if available
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = "processed.pdf"
        if "filename=" in content_disposition:
            # Extract filename from Content-Disposition
            filename_part = content_disposition.split("filename=")[1]
            if '"' in filename_part:
                filename = filename_part.split('"')[1]
            else:
                filename = filename_part.split(';')[0]
        
        # Return the file content as a streaming response
        return StreamingResponse(
            iter([response.content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"Error proxying PDF download: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Download error: {str(e)}"}
        )

# System status endpoint
@app.get("/status")
async def system_status():
    """Check the status of the system."""
    try:
        # Check MCP server status
        mcp_status = "Unknown"
        
        try:
            # Try multiple endpoints to check MCP server status
            endpoints_to_try = [
                "/api-status",  # Our custom status endpoint
                "/test",        # Our test endpoint
                "/",            # Root endpoint
                "/sse"          # SSE endpoint from MCP
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = await http_client.get(f"{mcp_server_url}{endpoint}")
                    if response.status_code == 200:
                        if endpoint == "/api-status":
                            mcp_data = response.json()
                            mcp_status = mcp_data.get("status", "OK")
                        else:
                            mcp_status = f"OK (via {endpoint} endpoint)"
                        break
                except Exception:
                    continue
            else:  # This executes if no endpoint succeeded
                mcp_status = "Error: Could not connect to MCP server"
        except Exception as e:
            mcp_status = f"Error: {str(e)}"
        
        return {
            "frontend": {
                "status": "running",
                "port": frontend_port
            },
            "mcp_server": {
                "status": mcp_status,
                "url": mcp_server_url
            }
        }
    except Exception as e:
        logger.error(f"Error checking system status: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await http_client.aclose()

# Run the app
def main():
    logger.info(f"Starting frontend server on port {frontend_port}")
    uvicorn.run(app, host="0.0.0.0", port=frontend_port)

if __name__ == "__main__":
    main()
