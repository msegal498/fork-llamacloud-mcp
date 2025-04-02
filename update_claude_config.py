import os
import json
import sys
import ctypes
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_claude_config():
    """Try to find Claude Desktop config in common locations"""
    possible_paths = [
        os.path.expandvars(r'%APPDATA%\Claude\config.json'),
        os.path.expandvars(r'%LOCALAPPDATA%\Claude\config.json'),
        os.path.expandvars(r'%USERPROFILE%\.claude\config.json'),
        r'C:\Program Files\Claude\config.json',
        r'C:\Program Files (x86)\Claude\config.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Claude config at: {path}")
            return path
    
    return None

def create_config(project_dir):
    """Create a new config with our debug tools"""
    return {
        "mcpServers": {
            "debug_script": {
                "command": "python",
                "args": [
                    os.path.join(project_dir, "debug_script.py")
                ]
            },
            "simple_mcp_server": {
                "command": "poetry",
                "args": [
                    "run",
                    "python",
                    os.path.join(project_dir, "simple_mcp_server.py")
                ],
                "cwd": project_dir
            },
            "llama_index_docs_server": {
                "command": "poetry",
                "args": [
                    "run",
                    "python", 
                    os.path.join(project_dir, "llamacloud_mcp", "mcp_server.py")
                ],
                "cwd": project_dir
            }
        }
    }

def main():
    # Get current project directory
    project_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"Project directory: {project_dir}")
    
    # Create config content
    config = create_config(project_dir)
    
    # Write to local file
    local_config_path = os.path.join(project_dir, "claude_desktop_config.json")
    with open(local_config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"Local config created at: {local_config_path}")
    print("\nThis file needs to be copied to Claude Desktop's config location.")
    
    # Try to find Claude config
    claude_config_path = find_claude_config()
    if not claude_config_path:
        print("\nCould not automatically find Claude Desktop config.")
        print("To manually update Claude Desktop config:")
        print("1. Open Claude Desktop")
        print("2. Go to Settings -> Developer -> Edit Config")
        print("3. Copy the content from the file below and paste it into Claude's config editor")
        print(f"   {local_config_path}")
        return
    
    # Ask user if they want to try updating the config automatically
    try_update = input(f"\nDo you want to try updating Claude config at {claude_config_path}? (y/n): ")
    if try_update.lower() != 'y':
        print("No changes made to Claude config.")
        return
    
    if not is_admin() and any(path in claude_config_path for path in ['Program Files', 'ProgramFiles']):
        print("This script needs admin rights to update the config in Program Files.")
        print("Please run this script as administrator or manually update the config.")
        return
    
    try:
        # Backup existing config
        if os.path.exists(claude_config_path):
            backup_path = claude_config_path + '.backup'
            with open(claude_config_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"Backed up existing config to: {backup_path}")
        
        # Write new config
        with open(claude_config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Updated Claude config at: {claude_config_path}")
        print("Please restart Claude Desktop for changes to take effect.")
    except Exception as e:
        print(f"Error updating Claude config: {str(e)}")
        print("Please update the config manually as described above.")

if __name__ == "__main__":
    main()
