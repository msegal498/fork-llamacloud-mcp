import os
import sys
import json
import subprocess
import traceback
sys.path.append("../../")  # Add the project root to path

def print_error(msg):
    print(f"ERROR: {msg}", file=sys.stderr)

# Print basic info
print("Claude Desktop Debug Script", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Python executable: {sys.executable}", file=sys.stderr)

# Print current directory and files
try:
    current_dir = os.getcwd()
    print(f"\nCurrent working directory: {current_dir}", file=sys.stderr)
    
    print("\nFiles in current directory:", file=sys.stderr)
    for file in os.listdir(current_dir):
        print(f"- {file}", file=sys.stderr)
except Exception as e:
    print_error(f"Error listing directory: {str(e)}")

# Check for pyproject.toml
try:
    if os.path.exists("../../pyproject.toml"):
        print("\npyproject.toml exists in project root", file=sys.stderr)
        with open("../../pyproject.toml", "r") as f:
            print("\nContents of pyproject.toml:", file=sys.stderr)
            print(f.read(), file=sys.stderr)
    else:
        print("\npyproject.toml does NOT exist in project root", file=sys.stderr)
        
        # Try parent directory
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(parent_dir, "pyproject.toml")):
            print(f"pyproject.toml exists in parent directory: {parent_dir}", file=sys.stderr)
except Exception as e:
    print_error(f"Error checking pyproject.toml: {str(e)}")

# Check if Poetry is installed
try:
    poetry_version = subprocess.check_output(["poetry", "--version"], universal_newlines=True).strip()
    print(f"\nPoetry version: {poetry_version}", file=sys.stderr)
except Exception as e:
    print_error(f"Error running Poetry: {str(e)}")
    
    # Check if Poetry is in PATH
    paths = os.environ.get("PATH", "").split(os.pathsep)
    print("\nSearching for Poetry in PATH:", file=sys.stderr)
    for path in paths:
        poetry_path = os.path.join(path, "poetry.exe")
        if os.path.exists(poetry_path):
            print(f"- Found at: {poetry_path}", file=sys.stderr)

# Print environment variables
try:
    print("\nRelevant environment variables:", file=sys.stderr)
    for key, value in os.environ.items():
        if any(keyword in key.lower() for keyword in ["path", "poetry", "python", "llama"]):
            print(f"- {key}: {value}", file=sys.stderr)
except Exception as e:
    print_error(f"Error printing environment variables: {str(e)}")

# Create simple MCP tool
try:
    from mcp.server.fastmcp import FastMCP
    
    print("\nMCP library is available!", file=sys.stderr)
    
    # Create and return a simple response
    print("\nThis script completed successfully", file=sys.stderr)
    print("If you can see this message, the basic communication with Claude Desktop is working", file=sys.stderr)
    
except ImportError:
    print_error("MCP library is not installed or not accessible.")
    print("\nTo install MCP library:", file=sys.stderr)
    print("1. Open command prompt", file=sys.stderr)
    print("2. Navigate to your project directory", file=sys.stderr)
    print("3. Run: poetry add mcp", file=sys.stderr)
except Exception as e:
    print_error(f"Unexpected error: {str(e)}")
    traceback.print_exc(file=sys.stderr)

# This is needed for Claude to see the debug info
print("Debug information has been written to Claude Desktop logs.")
