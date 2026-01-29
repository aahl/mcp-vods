import os
import logging
import argparse
import asyncio
import aiohttp
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from . import (
    vods,
    moon,
    mitv,
    tvbox,
)

_LOGGER = logging.getLogger(__name__)


async def async_main():
    port = int(os.getenv("PORT", 0)) or 80
    parser = argparse.ArgumentParser(description="MCP Server for Binge-watch")
    parser.add_argument("--http", action="store_true", help="Use streamable HTTP mode instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=port, help=f"Port to listen on (default: {port})")

    args = parser.parse_args()

    mcp = FastMCP(name="mcp-vods", version="0.1.9")

    async with aiohttp.ClientSession() as session:
        await vods.add_tools(mcp, session, _LOGGER)
        await moon.add_tools(mcp, session, _LOGGER)
        await mitv.add_tools(mcp, session, _LOGGER)
        await tvbox.add_tools(mcp, session, _LOGGER)

        mode = os.getenv("TRANSPORT") or ("http" if args.http else None)
        if mode in ["http", "sse"]:
            app = mcp.http_app(transport=mode)
            app.add_middleware(
                CORSMiddleware,
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*"],
                allow_origins=["*"],
                allow_credentials=True,
                expose_headers=["mcp-session-id", "mcp-protocol-version"],
                max_age=86400,
            )
            await mcp.run_async(transport=mode, host=args.host, port=args.port)
        else:
            await mcp.run_async()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
