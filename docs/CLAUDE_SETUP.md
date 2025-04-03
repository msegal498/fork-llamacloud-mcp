# Setting Up Claude Desktop with LlamaCloud MCP

This guide will help you correctly configure Claude Desktop to work with the LlamaCloud MCP tools.

## Troubleshooting the Current Setup

Based on the error logs, there are two main issues:

1. **Poetry can't find the pyproject.toml file** - The path in the Claude Desktop config is incorrect
2. **npm errors** - There might be a conflict with another MCP server config

## Step 1: Update Claude Desktop Configuration

### Automatic Method:

1. Run the `update_claude_config.py` script:
   ```
   python update_claude_config.py
   ```

2. This script will:
   - Create a properly formatted configuration file
   - Attempt to locate Claude Desktop's config file
   - Offer to update it automatically if found

### Manual Method:

1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Replace the entire configuration with the following:

```json
{
    "mcpServers": {
        "debug_script": {
            "command": "python",
            "args": [
                "C:\\Users\\maxse\\OneDrive\\Desktop\\LlamaCloud-MCP\\fork-llamacloud-mcp\\debug_script.py"
            ]
        },
        "simple_mcp_server": {
            "command": "poetry",
            "args": [
                "run",
                "python",
                "C:\\Users\\maxse\\OneDrive\\Desktop\\LlamaCloud-MCP\\fork-llamacloud-mcp\\simple_mcp_server.py"
            ],
            "cwd": "C:\\Users\\maxse\\OneDrive\\Desktop\\LlamaCloud-MCP\\fork-llamacloud-mcp"
        },
        "llama_index_docs_server": {
            "command": "poetry",
            "args": [
                "run",
                "python", 
                "C:\\Users\\maxse\\OneDrive\\Desktop\\LlamaCloud-MCP\\fork-llamacloud-mcp\\llamacloud_mcp\\mcp_server.py"
            ],
            "cwd": "C:\\Users\\maxse\\OneDrive\\Desktop\\LlamaCloud-MCP\\fork-llamacloud-mcp"
        }
    }
}
```

## Step 2: Restart Claude Desktop

After updating the configuration, completely close and restart Claude Desktop.

## Step 3: Test the Tools in Order

Test the tools in the following order to diagnose any remaining issues:

1. First test the **debug_script** tool
   - This will print diagnostic information to help identify path issues
   
2. Then test the **simple_mcp_server** tool
   - This is a minimal MCP implementation to test basic connectivity
   
3. Finally test the **llama_index_docs_server** tool
   - This is the full implementation with LlamaCloud integration

## Step 4: Check the Logs

If you encounter errors, check the logs in Claude Desktop:

1. Open Claude Desktop
2. Go to Settings → Developer → View Logs
3. Look for errors related to your MCP servers

## Common Issues and Solutions

### Poetry Not Found

If Poetry is not in your PATH:

1. Install Poetry using the official installer: https://python-poetry.org/docs/#installation
2. Make sure it's added to your PATH
3. Restart your computer after installation

### pyproject.toml Not Found

If Poetry can't find the pyproject.toml file:

1. Make sure the `cwd` value in the configuration points to the directory containing pyproject.toml
2. Check that the pyproject.toml file exists in the project directory

### npm Errors

If you see npm errors:

1. Check if you have multiple MCP server configurations in Claude Desktop
2. Remove any npm-based configurations that might be conflicting

## Need Further Assistance?

If you continue to experience issues:

1. Try running the MCP server directly from command line:
   ```
   cd C:\Users\maxse\OneDrive\Desktop\LlamaCloud-MCP\fork-llamacloud-mcp
   poetry run python llamacloud_mcp\mcp_server.py
   ```

2. See if there are any errors in the direct execution
