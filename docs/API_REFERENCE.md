# API Reference

## MCP Server API

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Server-Sent Events (SSE)

```
GET /sse
```

This endpoint provides real-time communication between the client and server. It outputs periodic pings and event data.

#### MCP Tools

The MCP server exposes the following tools through the MCP protocol:

##### llama_index_documentation

Searches the LlamaIndex documentation for the given query.

**Input:**
- `query` (string): The query to search for in the LlamaIndex documentation.

**Output:**
- Response text from the LlamaCloud index.

## Frontend Server API

### Base URL

```
http://localhost:8080
```

### Endpoints

#### Home Page

```
GET /
```

Serves the main web interface.

#### Query Endpoint

```
POST /query
```

Sends queries to be processed by LlamaCloud.

**Request Body:**
```json
{
  "query": "string"
}
```

**Response:**
```json
{
  "response": "string"
}
```

or in case of error:

```json
{
  "error": "string"
}
```

#### Status Endpoint

```
GET /status
```

Provides system status information.

**Response:**
```json
{
  "services": {
    "mcp_server": "string",
    "llama_cloud": "string"
  },
  "environment": {
    "frontend_port": "number",
    "mcp_server_url": "string",
    "mcp_server_port": "string",
    "llama_cloud_index": "string"
  }
}
```
