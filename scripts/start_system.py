"""
Start script for the PDF Chunking System.
This script provides commands to start different components of the system.
"""

import os
import sys
import subprocess
import argparse
import signal
import time
import logging
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Set working directory to project root
os.chdir(PROJECT_ROOT)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
env_path = PROJECT_ROOT / "config" / ".env"
load_dotenv(dotenv_path=str(env_path))
logger.info(f"Loaded environment from {env_path}")

def start_mcp_http_server():
    """Start the MCP HTTP Server."""
    sys.path.insert(0, str(PROJECT_ROOT))  # Ensure project root is in path
    from backend.api.mcp_http_server import main
    logger.info("Starting MCP HTTP Server...")
    main()

def start_frontend_server():
    """Start the Frontend Server."""
    sys.path.insert(0, str(PROJECT_ROOT))  # Ensure project root is in path
    from frontend.server.frontend_server import main
    logger.info("Starting Frontend Server...")
    main()

def start_all():
    """Start all system components in separate processes."""
    processes = []
    
    try:
        # Create data directories if they don't exist
        data_dir = PROJECT_ROOT / "data"
        uploads_dir = data_dir / "uploads"
        outputs_dir = data_dir / "outputs"
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(outputs_dir, exist_ok=True)
        logger.info(f"Ensured data directories exist: {uploads_dir}, {outputs_dir}")
        
        # Start MCP HTTP Server in a subprocess
        logger.info("Starting MCP HTTP Server in subprocess...")
        mcp_http_cmd = [sys.executable, "-m", "backend.api.mcp_http_server"]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        mcp_http_proc = subprocess.Popen(mcp_http_cmd, env=env, cwd=str(PROJECT_ROOT))
        processes.append(("MCP HTTP Server", mcp_http_proc))
        
        # Give the MCP HTTP Server time to start
        time.sleep(2)
        
        # Start Frontend Server in a subprocess
        logger.info("Starting Frontend Server in subprocess...")
        frontend_cmd = [sys.executable, "-m", "frontend.server.frontend_server"]
        frontend_proc = subprocess.Popen(frontend_cmd, env=env, cwd=str(PROJECT_ROOT))
        processes.append(("Frontend Server", frontend_proc))
        
        # Wait for user to press Ctrl+C
        logger.info("\n" + "-" * 40)
        logger.info("PDF Chunking System is running.")
        logger.info("Frontend is available at: http://localhost:8080")
        logger.info("Press Ctrl+C to stop all servers.")
        logger.info("-" * 40 + "\n")
        
        # Keep the main process running until interrupted
        while all(p.poll() is None for _, p in processes):
            time.sleep(1)
        
        # Check if any process exited prematurely
        for name, proc in processes:
            if proc.poll() is not None:
                logger.error(f"{name} exited unexpectedly with code {proc.returncode}")
        
    except KeyboardInterrupt:
        logger.info("\nShutting down all servers...")
    finally:
        # Clean up all processes
        for name, proc in processes:
            if proc.poll() is None:
                logger.info(f"Terminating {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} did not terminate gracefully, killing...")
                    proc.kill()
        
        logger.info("All servers have been shut down.")

def main():
    """Main entry point for the start script."""
    parser = argparse.ArgumentParser(description="PDF Chunking System Starter")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Start all servers
    all_parser = subparsers.add_parser("all", help="Start all system components")
    
    # Start MCP HTTP server only
    mcp_http_parser = subparsers.add_parser("mcp-http", help="Start MCP HTTP Server only")
    
    # Start frontend server only
    frontend_parser = subparsers.add_parser("frontend", help="Start Frontend Server only")
    
    args = parser.parse_args()
    
    if args.command == "all" or args.command is None:
        start_all()
    elif args.command == "mcp-http":
        start_mcp_http_server()
    elif args.command == "frontend":
        start_frontend_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
