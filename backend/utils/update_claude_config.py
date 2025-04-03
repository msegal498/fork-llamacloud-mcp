"""
Update Claude Desktop configuration to include the MCP server.
"""
import os
import json
import sys
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path for imports
sys.path.append("../../")

def update_claude_config(config_path=None, claude_executable=None):
    """
    Update the Claude Desktop configuration to include the MCP server.
    
    Args:
        config_path (str, optional): Path to claude_desktop_config.json. If None, uses default location.
        claude_executable (str, optional): Path to Claude executable. If None, searches common locations.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Determine default config path if not provided
    if config_path is None:
        config_path = "../../config/claude_desktop_config.json"
    
    try:
        # Load existing config if it exists
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded existing config from {config_path}")
        else:
            # Create a new config file
            config = {}
            logger.info(f"Creating new config at {config_path}")
        
        # Update or add the MCP server configuration
        mcp_config = {
            "server": "simple",
            "pythonCommand": sys.executable,
            "scriptPath": os.path.abspath("../api/simple_mcp_server.py")
        }
        
        # Add or update the MCP configuration
        if "mcp" not in config:
            config["mcp"] = mcp_config
            logger.info("Added MCP configuration")
        else:
            config["mcp"].update(mcp_config)
            logger.info("Updated MCP configuration")
        
        # Set Claude executable path if provided
        if claude_executable:
            config["claudePath"] = claude_executable
            logger.info(f"Set Claude executable path to {claude_executable}")
        
        # Save the updated configuration
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            logger.info(f"Saved updated configuration to {config_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating Claude configuration: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Claude Desktop configuration for MCP")
    parser.add_argument("--config", help="Path to the Claude Desktop configuration file")
    parser.add_argument("--claude-path", help="Path to the Claude Desktop executable")
    args = parser.parse_args()
    
    success = update_claude_config(args.config, args.claude_path)
    
    if success:
        print("Claude Desktop configuration updated successfully!")
    else:
        print("Failed to update Claude Desktop configuration. Check the logs for details.")
        sys.exit(1)
