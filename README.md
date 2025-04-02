# LlamaCloud MCP Integration

This repository provides tools to integrate LlamaCloud with Claude Desktop via the Machine Chat Protocol (MCP). It allows Claude to search and retrieve information from LlamaIndex documentation stored in a LlamaCloud index.

![Claude Logo](claude.png)

## Features

- **Claude Desktop Integration**: Connect Claude Desktop to your LlamaCloud indexes
- **LlamaIndex Documentation Search**: Query LlamaIndex documentation using natural language
- **Multiple Server Options**: Choose between simple stdio-based servers or HTTP servers
- **Debugging Tools**: Helper scripts to troubleshoot your setup

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Claude Desktop
- LlamaCloud account with an existing index
- OpenAI API key (for the client demo)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/llamacloud-mcp.git
cd llamacloud-mcp
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Configure Environment Variables

1. Copy the sample `.env` file and fill in your credentials:

```
# LlamaCloud Configuration
LLAMA_CLOUD_INDEX_NAME="your-index-name"
LLAMA_CLOUD_PROJECT_NAME="Your Project"
LLAMA_CLOUD_ORG_ID="your-organization-id"
LLAMA_CLOUD_API_KEY="your-llamacloud-api-key"

# MCP Server Configuration
MCP_SERVER_URL="http://localhost:8000/sse"
MCP_SERVER_PORT="8000"
MCP_SERVER_NAME="llama-index-server"

# OpenAI API Key (for client demo)
OPENAI_API_KEY="your-openai-api-key"
```

### 4. Configure Claude Desktop

Follow the instructions in [CLAUDE_SETUP.md](CLAUDE_SETUP.md) to properly configure Claude Desktop to work with this MCP server.

You can use the provided script to automatically update your Claude Desktop configuration:

```bash
python update_claude_config.py
```

## Usage

### Running the MCP Server (stdio for Claude Desktop)

```bash
poetry run python llamacloud_mcp/mcp_server.py
```

### Running the HTTP Server (for API clients)

```bash
poetry run python mcp_http_server.py
```

### Testing with Debug Script

```bash
python debug_script.py
```

### Testing with MCP Client

```bash
poetry run python mcp-client.py "What is LlamaIndex?"
```

## Server Types

This repository includes multiple server implementations:

1. **`simple_mcp_server.py`**: A minimal MCP server for testing Claude Desktop connectivity
2. **`llamacloud_mcp/mcp_server.py`**: The main stdio-based MCP server for Claude Desktop
3. **`mcp_http_server.py`**: HTTP server for programmatic clients

## Troubleshooting

If you're experiencing issues:

1. Run the **debug_script.py** to check your environment setup
2. Ensure Poetry is correctly installed and in your PATH
3. Verify that all required environment variables are set
4. Check Claude Desktop logs for detailed error messages
5. See [CLAUDE_SETUP.md](CLAUDE_SETUP.md) for detailed troubleshooting steps

## How It Works

1. The MCP server exposes a `llama_index_documentation` tool that accepts natural language queries
2. When invoked, the tool connects to your LlamaCloud index using the provided credentials
3. The query is processed by the LlamaCloud index, retrieving relevant documentation
4. The response is returned to Claude, which can then provide you with the information

## Components

- **`llamacloud_mcp/mcp_server.py`**: Main MCP server implementation
- **`mcp_http_server.py`**: HTTP server implementation
- **`simple_mcp_server.py`**: Diagnostic MCP server
- **`debug_script.py`**: Environment verification tool
- **`update_claude_config.py`**: Claude Desktop configuration utility
- **`mcp-client.py`**: Example client using OpenAI to interact with the MCP server

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## PDF Chunking & Summarization Tool

Based on the included implementation plan, there are plans to develop a PDF chunking and summarization tool with the following architecture:

```
[ Frontend Website (HTML/JS) ]
          │
          ▼
[ Backend API (Python: FastAPI) ]
          │
          ▼
[ LlamaIndex + OpenAI API ]
    ├── PDF Parsing (pdfplumber)
    ├── Chunking (LlamaIndex)
    ├── Recursive Summarization (LlamaIndex)
    └── PDF Export (pdfkit)
```

See the implementation plan document for detailed information on this upcoming feature.