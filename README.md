# PDF Chunking System

This project provides a PDF chunking system built on top of the LlamaCloud-MCP integration. It allows users to upload PDF files, process them (extract text, chunk it, and summarize content), and download the processed results.

## Architecture

The system consists of the following components:

### Backend
- **MCP Server**: Core server with stdio transport for local CLI usage
- **MCP HTTP Server**: REST API for PDF processing operations
- **Shared Client**: Common functionality for LlamaCloud/OpenAI interaction and PDF processing
- **PDF Processor**: Utilities for text extraction, chunking, and PDF generation

### Frontend
- **Web Interface**: User-friendly interface for uploading and processing PDFs
- **Frontend Server**: Proxies requests to the MCP HTTP Server and handles file uploads/downloads

## Installation

1. Clone this repository
2. Set up your Python environment with Poetry (Python 3.11+ recommended):

```bash
# Install dependencies using Poetry
poetry install
```

3. Set up your environment variables in `config/.env`:

```
# Server Configuration
FRONTEND_PORT=8080
MCP_SERVER_PORT=8000
MCP_SERVER_NAME=pdf-chunking-server
MCP_SERVER_URL=http://localhost:8000

# LlamaCloud Configuration
LLAMA_CLOUD_API_KEY=your_api_key_here
LLAMA_CLOUD_ORG_ID=your_org_id_here
LLAMA_CLOUD_PROJECT_NAME=your_project_name_here
LLAMA_CLOUD_INDEX_NAME=your_index_name_here

# OpenAI Configuration (for summarization)
OPENAI_API_KEY=your_openai_api_key_here

# PDF Processing Configuration
PDF_UPLOAD_DIR=./data/uploads
PDF_OUTPUT_DIR=./data/outputs
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
```

## Usage

### Starting the System

The easiest way to start the system is to use the provided start script:

```bash
# Start all components
poetry run python -m scripts.start_system all

# Or simply
poetry run python -m scripts.start_system
```

You can then access the web interface at:

```
http://localhost:8080
```

### Running Components Separately

If you prefer to run the components separately:

**Using Poetry Run Scripts:**
```bash
# Start MCP HTTP Server
poetry run start-mcp-http

# Start Frontend Server
poetry run start-frontend
```

**Or using Python modules:**
```bash
# Start MCP HTTP Server only
poetry run python -m scripts.start_system mcp-http

# Start Frontend Server only
poetry run python -m scripts.start_system frontend
```

### Processing PDFs

1. Open your browser and navigate to `http://localhost:8080`
2. Upload a PDF file using the web interface
3. The system will process the PDF and display status updates
4. Once processing is complete, download the summarized PDF

### CLI Usage

For development and testing, you can use the local client directly:

```bash
# Start the MCP Server with stdio transport
poetry run start-mcp-server
```

## Project Structure

```
fork-llamacloud-mcp/
│
├── backend/                          # Backend components
│   ├── api/                          # API endpoints
│   │   └── mcp_http_server.py        # MCP HTTP server
│   │
│   ├── clients/                      # Client implementations
│   │   ├── shared_llama_client.py    # Shared functionality
│   │   ├── mcp_client_local.py       # Local client for CLI
│   │   └── mcp_client_remote.py      # Remote client for web
│   │
│   ├── llamacloud_mcp/               # Core package
│   │   └── mcp_server.py             # Core MCP implementation
│   │
│   └── utils/                        # Utility functions
│       └── pdf_processor.py          # PDF processing utilities
│
├── frontend/                         # Frontend components
│   ├── server/                       # Frontend server
│   │   └── frontend_server.py        # FastAPI server
│   │
│   └── static/                       # Static assets
│       ├── css/                      # CSS stylesheets
│       │   └── styles.css            # Main stylesheet
│       ├── js/                       # JavaScript files
│       │   └── main.js               # Frontend logic
│       └── index.html                # Main HTML template
│
├── data/                             # Data directories
│   ├── uploads/                      # Uploaded PDF files
│   └── outputs/                      # Processed PDF files
│
├── config/                           # Configuration files
│   └── .env                          # Environment variables
│
├── scripts/                          # Utility scripts
│   └── start_system.py               # System startup script
│
├── poetry.lock                       # Poetry lock file
├── pyproject.toml                    # Project configuration
└── README.md                         # This file
```

## Troubleshooting

If you encounter issues:

1. Make sure all required environment variables are set in the `config/.env` file
2. Check that the MCP HTTP server is running on port 8000
3. Check that the frontend server is running on port 8080
4. Confirm that your LlamaCloud/OpenAI API keys are valid
5. Ensure that the required Python packages are installed via Poetry
6. Check the system status at http://localhost:8080/status

### Running without API Keys

If you want to test the system without setting up API keys, you can use the fallback configuration:

```bash
# Copy the fallback configuration (no API keys required)
copy config\.env.fallback config\.env

# Run the system
poetry run start
```

In fallback mode, the following limitations apply:
- Documentation search will not work (returns error messages)
- Summarization will use a basic text extraction algorithm instead of AI
- The system will still extract text, chunk it, and generate PDFs

## Dependencies

The system relies on the following key dependencies:
- FastAPI and Uvicorn for web servers
- PyPDF2 for PDF text extraction
- ReportLab for PDF generation
- LlamaIndex for LlamaCloud integration
- OpenAI for text summarization
- MCP for server/client communication
