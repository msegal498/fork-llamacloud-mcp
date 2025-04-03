"""
Environment test script for PDF Chunking System.
This script checks that all required paths and dependencies are available.
"""

import os
import sys
import importlib.util
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
logger.info(f"Project root: {PROJECT_ROOT}")

# Check Python path
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")

# Add project root to path
sys.path.insert(0, str(PROJECT_ROOT))
logger.info(f"Python path: {sys.path}")

def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        logger.info(f"✅ Module {module_name} imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import {module_name}: {str(e)}")
        return False

def check_path(path):
    """Check if a path exists."""
    full_path = PROJECT_ROOT / path
    if full_path.exists():
        logger.info(f"✅ Path exists: {full_path}")
        return True
    else:
        logger.error(f"❌ Path does not exist: {full_path}")
        return False

def main():
    """Run all environment tests."""
    logger.info("Starting environment tests...")
    
    # Check key directories
    check_path("config")
    check_path("config/.env")
    check_path("frontend/static")
    check_path("frontend/static/index.html")
    check_path("frontend/static/css/styles.css")
    check_path("frontend/static/js/main.js")
    check_path("data/uploads")
    check_path("data/outputs")
    
    # Check key modules
    check_module("backend.api.mcp_http_server")
    check_module("frontend.server.frontend_server")
    check_module("backend.clients.shared_llama_client")
    check_module("backend.utils.pdf_processor")
    
    # Check environment variables
    env_vars = [
        "FRONTEND_PORT",
        "MCP_SERVER_PORT",
        "MCP_SERVER_URL",
        "PDF_UPLOAD_DIR",
        "PDF_OUTPUT_DIR"
    ]
    
    logger.info("Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=str(PROJECT_ROOT / "config" / ".env"))
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var} = {value}")
        else:
            logger.warning(f"⚠️ {var} not set")
    
    logger.info("Environment tests completed.")

if __name__ == "__main__":
    main()
