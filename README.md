# Mock MCP Server

A minimal MCP (Model Context Protocol) server for testing. Provides simple, deterministic tools useful for validating MCP client integrations.

## Quick Start

```bash
docker run -p 8000:8000 -e TRANSPORT=streamable-http arcadyt/mock-mcp-server
```

Or with stdio transport:

```bash
docker run -i arcadyt/mock-mcp-server
```

## Tools

| Tool | Description |
|------|-------------|
| `echo` | Echo back the input message |
| `random_number` | Generate random int (with optional seed for determinism) |
| `timestamp` | Return current UTC timestamp |
| `whoami` | Return session info and API key status |
| `env_check` | Check if an environment variable is set |
| `validate_credentials` | Validate that `MOCK_API_KEY` is configured |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `TRANSPORT` | `stdio` | Transport protocol: `stdio` or `streamable-http` |
| `MOCK_API_KEY` | (none) | Optional API key for credential testing |

## Usage Examples

### Test with Claude Code

Add to your MCP settings:

```json
{
  "mcpServers": {
    "mock": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Test Credential Injection

```bash
docker run -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e MOCK_API_KEY=test-secret-123 \
  arcadyt/mock-mcp-server
```

Then call `whoami` or `validate_credentials` to verify the key was injected.

## Building Locally

```bash
docker build -t mock-mcp-server .
docker run -p 8000:8000 -e TRANSPORT=streamable-http mock-mcp-server
```

## License

MIT
