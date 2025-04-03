# Getting Started with PDF Chunking System

This guide will help you get the PDF Chunking System up and running quickly.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- API keys for LlamaCloud and/or OpenAI

## Step 1: Install Dependencies

```bash
# Install all dependencies using Poetry
poetry install
```

## Step 2: Configure Environment

1. Edit the `.env` file in the `config` directory:

```
# Server Configuration
FRONTEND_PORT=8080
MCP_SERVER_PORT=8000
MCP_SERVER_NAME=pdf-chunking-server
MCP_SERVER_URL=http://localhost:8000

# LlamaCloud Configuration (required for documentation search)
LLAMA_CLOUD_API_KEY=your_api_key_here
LLAMA_CLOUD_ORG_ID=your_org_id_here
LLAMA_CLOUD_PROJECT_NAME=your_project_name_here
LLAMA_CLOUD_INDEX_NAME=your_index_name_here

# OpenAI Configuration (required for PDF summarization)
OPENAI_API_KEY=your_openai_api_key_here

# PDF Processing Configuration
PDF_UPLOAD_DIR=./data/uploads
PDF_OUTPUT_DIR=./data/outputs
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
```

## Step 3: Test the Environment

Run the environment test to ensure everything is set up correctly:

```bash
poetry run test-env
```

This will check for required paths, modules, and environment variables.

## Step 4: Start the System

Start all components with a single command:

```bash
poetry run start
```

This will start:
- The MCP HTTP Server on port 8000
- The Frontend Server on port 8080

You can access the web interface at: http://localhost:8080

## Alternative Startup Methods

You can start individual components if needed:

```bash
# Start only the MCP HTTP Server
poetry run start-mcp-http

# Start only the Frontend Server
poetry run start-frontend

# Use the script with specific commands
poetry run python -m scripts.start_system mcp-http
poetry run python -m scripts.start_system frontend
```

## Troubleshooting

If you encounter issues:

1. **Check logs in the console window** - error messages will be displayed
2. **Verify API keys** - ensure LlamaCloud and OpenAI keys are correct
3. **Check ports** - make sure ports 8000 and 8080 are available
4. **Check file paths** - verify that data directories are accessible

For more detailed troubleshooting, refer to the README.md file.

## Next Steps

- Try uploading a small PDF (less than 5MB) first
- Experiment with different chunk sizes in the .env file
- Set up custom development environments with Poetry
