# Troubleshooting Guide for PDF Chunking System

This guide provides solutions for common issues you might encounter when setting up and running the PDF Chunking System.

## Common Issues

### 1. Error: Module Not Found

**Symptoms:**
- Error message containing `ModuleNotFoundError` or `ImportError`
- References to missing packages like `mcp`, `llama_index`, etc.

**Solutions:**
- Ensure you've installed all dependencies with Poetry: `poetry install`
- Activate the Poetry environment: `poetry shell`
- Make sure you're using Poetry to run commands: `poetry run start`

### 2. MCP Server Initialization Issues

**Symptoms:**
- `AttributeError: 'FastMCP' object has no attribute 'app'`
- `TypeError: FastMCP.__init__() got an unexpected keyword argument 'port'`

**Solutions:**
- The system includes fallbacks for different versions of MCP
- If you have a version compatibility issue, check the MCP documentation and update the code accordingly
- Try running directly with uvicorn: `uvicorn backend.api.mcp_http_server:app --host 0.0.0.0 --port 8000`

### 3. API Key Issues

**Symptoms:**
- Error messages about invalid API keys
- LlamaCloud or OpenAI initialization failures

**Solutions:**
- Check that your API keys are properly set in `config/.env`
- If you're just testing, use the fallback mode which works without API keys: `copy config\.env.fallback config\.env`
- In fallback mode, summarization uses basic text extraction instead of AI

### 4. Port Already in Use

**Symptoms:**
- `Address already in use` errors
- Server fails to start

**Solutions:**
- Check for other processes using ports 8000 and 8080
- Close any other web servers or applications that might be using these ports
- Change the ports in `config/.env` if needed:
  ```
  FRONTEND_PORT=8081  # Changed from 8080
  MCP_SERVER_PORT=8001  # Changed from 8000
  MCP_SERVER_URL=http://localhost:8001  # Update to match MCP_SERVER_PORT
  ```

### 5. File Upload Issues

**Symptoms:**
- Uploads fail or time out
- Files appear to upload but processing fails

**Solutions:**
- Ensure the `data/uploads` and `data/outputs` directories exist
- Check file permissions on these directories
- Start with smaller PDFs (under 5MB) for testing
- Check if any antivirus software is blocking file access

### 6. PDF Processing Failures

**Symptoms:**
- Error messages about PDF processing
- Status shows "error" after upload

**Solutions:**
- Check if the PDF is password-protected (not supported)
- Try with a different PDF file
- Look for specific error messages in the console/logs
- Verify that PyPDF2 and ReportLab are properly installed

## Advanced Troubleshooting

### Checking Module Imports

If you're having import issues, you can run this Python snippet to verify imports:

```python
import importlib

modules = [
    "mcp.server.fastmcp",
    "llama_index.indices.managed.llama_cloud",
    "llama_index.llms.openai",
    "PyPDF2",
    "reportlab",
    "fastapi",
    "uvicorn"
]

for module in modules:
    try:
        importlib.import_module(module)
        print(f"✅ Module {module} imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import {module}: {str(e)}")
```

### Environment Variables

To check if environment variables are properly loaded:

```python
import os
from dotenv import load_dotenv

load_dotenv("config/.env")

# Check key environment variables
variables = [
    "FRONTEND_PORT",
    "MCP_SERVER_PORT",
    "MCP_SERVER_URL",
    "LLAMA_CLOUD_API_KEY",
    "OPENAI_API_KEY",
    "PDF_UPLOAD_DIR",
    "PDF_OUTPUT_DIR"
]

for var in variables:
    value = os.getenv(var)
    if value:
        # Don't print full API keys
        if "API_KEY" in var and value != "not-used":
            print(f"✅ {var} is set (value hidden)")
        else:
            print(f"✅ {var} = {value}")
    else:
        print(f"❌ {var} is not set")
```

### Working Directory Issues

Working directory issues are common when using Poetry. Here's how to check and fix:

```python
import os
from pathlib import Path

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Project root should contain these key files/directories
expected_files = ["pyproject.toml", "config", "backend", "frontend"]
for file in expected_files:
    if os.path.exists(file):
        print(f"✅ {file} found")
    else:
        print(f"❌ {file} not found")

# Find project root
current_dir = Path(os.getcwd())
found = False
for parent in [current_dir] + list(current_dir.parents):
    if (parent / "pyproject.toml").exists():
        print(f"Project root appears to be: {parent}")
        found = True
        break

if not found:
    print("❌ Could not find project root directory")
```

### Path Resolution Issues

If you have path resolution issues:

1. Make sure you're running from the project root directory
2. Set the working directory explicitly in your code:

```python
import os
from pathlib import Path

# Find and set project root
project_root = None
current_dir = Path(__file__).resolve().parent
while current_dir != current_dir.parent:
    if (current_dir / "pyproject.toml").exists():
        project_root = current_dir
        break
    current_dir = current_dir.parent

if project_root:
    os.chdir(project_root)
    print(f"Set working directory to: {project_root}")
else:
    print("Could not find project root")
```

## Getting Support

If you're still having issues:

1. Check for error messages in the console window
2. Run with detailed logging: `poetry run python -m scripts.start_system 2> debug_log.txt`
3. Check the status endpoint: http://localhost:8080/status
4. Try the fallback mode to isolate API vs. code issues
5. Verify the installation with: `poetry run test-env`

When reporting issues, include:
- Full error message and stack trace
- Your environment (OS, Python version)
- Steps to reproduce the problem
- Any changes you've made to the code
