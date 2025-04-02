import os
import sys
import traceback

# Print diagnostic information to stderr so it shows up in Claude logs
print("Simple MCP Server starting...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Python executable: {sys.executable}", file=sys.stderr)

try:
    # Print current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}", file=sys.stderr)
    
    # Print files in current directory
    print("Files in current directory:", file=sys.stderr)
    for file in os.listdir(cwd):
        print(f"- {file}", file=sys.stderr)
        
    # Check for important files
    print("\nChecking for key files:", file=sys.stderr)
    key_files = ["pyproject.toml", ".env", "mcp_http_server.py"]
    for file in key_files:
        if os.path.exists(file):
            print(f"✓ {file} found", file=sys.stderr)
        else:
            print(f"✗ {file} NOT found", file=sys.stderr)
    
    # Import MCP
    print("\nImporting MCP library...", file=sys.stderr)
    try:
        from mcp.server.fastmcp import FastMCP
        print("✓ MCP library imported successfully", file=sys.stderr)
    except ImportError as e:
        print(f"✗ Error importing MCP: {str(e)}", file=sys.stderr)
        print("\nTrying to find mcp package...", file=sys.stderr)
        for path in sys.path:
            mcp_path = os.path.join(path, "mcp")
            if os.path.exists(mcp_path):
                print(f"- Found at: {mcp_path}", file=sys.stderr)
        raise
    
    # Create a simple MCP server
    print("\nCreating MCP server...", file=sys.stderr)
    mcp = FastMCP('simple-server')

    @mcp.tool()
    def echo(message: str) -> str:
        """Simply echoes back the message sent."""
        print(f"Echo tool called with: {message}", file=sys.stderr)
        return f"Echo: {message}"

    print("\nStarting MCP server with stdio transport...", file=sys.stderr)
    mcp.run(transport="stdio")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}", file=sys.stderr)
    print("\nFull traceback:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Exit with error code so Claude sees the failure
    sys.exit(1)
