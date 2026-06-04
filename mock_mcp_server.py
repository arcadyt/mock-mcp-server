#!/usr/bin/env python3
"""
Mock MCP Server for Testing

A minimal MCP server that supports both stdio and streamable-http transports.
Provides simple, deterministic tools for testing the mcp-gateway infrastructure.

Usage:
    python mock_mcp_server.py --transport=stdio
    python mock_mcp_server.py --transport=streamable-http --port=8000
"""
import os
import random
import sys
from datetime import UTC, datetime

import click
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

SERVER_NAME = "mock-mcp-server"
SERVER_VERSION = "1.0.0"

mcp = FastMCP(
    SERVER_NAME,
    instructions=(
        "Mock MCP server for testing. Provides simple tools: "
        "echo, random_number, timestamp, whoami, env_check, validate_credentials."
    ),
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


def _get_api_key() -> str | None:
    return os.environ.get("MOCK_API_KEY")


def _require_api_key() -> str:
    key = _get_api_key()
    if not key:
        raise ValueError("MOCK_API_KEY environment variable not set")
    return key


@mcp.tool()
def echo(message: str) -> str:
    """Echo the input message back. Useful for basic connectivity testing."""
    return f"Echo: {message}"


@mcp.tool()
def random_number(min_value: int = 0, max_value: int = 100, seed: int | None = None) -> int:
    """
    Generate a random integer between min_value and max_value (inclusive).

    If seed is provided, the result is deterministic for testing.
    """
    if seed is not None:
        random.seed(seed)
    return random.randint(min_value, max_value)


@mcp.tool()
def timestamp() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


@mcp.tool()
def whoami() -> dict:
    """
    Return information about the current session.

    Includes the API key (masked) to verify credential injection works.
    """
    api_key = _get_api_key()
    if api_key and len(api_key) >= 8:
        preview = f"{api_key[:4]}...{api_key[-4:]}"
    elif api_key:
        preview = "[too short]"
    else:
        preview = "[not set]"
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "api_key_present": api_key is not None,
        "api_key_preview": preview,
    }


@mcp.tool()
def env_check(variable_name: str) -> dict:
    """
    Check if an environment variable is set (without exposing the value).

    Useful for testing credential injection from Vault.
    """
    value = os.environ.get(variable_name)
    return {
        "variable": variable_name,
        "is_set": value is not None,
        "length": len(value) if value else 0,
    }


@mcp.tool()
def validate_credentials() -> dict:
    """
    Validate that required credentials are present.

    Returns success if MOCK_API_KEY is set, otherwise returns an error status.
    """
    try:
        key = _require_api_key()
        return {
            "status": "valid",
            "message": "Credentials validated successfully",
            "key_length": len(key),
        }
    except ValueError as e:
        return {
            "status": "invalid",
            "message": str(e),
        }


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http"]),
    default=None,
    help="Transport protocol. Defaults to TRANSPORT env var or 'stdio'.",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port for streamable-http transport (default: 8000).",
)
@click.option(
    "--host",
    type=str,
    default="0.0.0.0",
    help="Host for streamable-http transport (default: 0.0.0.0).",
)
def main(transport: str | None, port: int, host: str) -> int:
    """Run the mock MCP server."""
    resolved_transport = transport or os.environ.get("TRANSPORT", "stdio")

    if resolved_transport == "streamable-http":
        import uvicorn

        mcp.settings.host = host
        mcp.settings.port = port

        print(f"Starting mock MCP server (streamable-http) on {host}:{port}", file=sys.stderr)
        app = mcp.streamable_http_app()
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        import anyio

        print("Starting mock MCP server (stdio)", file=sys.stderr)
        anyio.run(mcp.run_stdio_async)

    return 0


if __name__ == "__main__":
    sys.exit(main())
