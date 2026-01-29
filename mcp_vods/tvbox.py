import os
import json
import aiohttp
import asyncio
from fastmcp import FastMCP
from pydantic import Field

TVBOX_LOCAL_IP = str(os.getenv("TVBOX_LOCAL_IP", "")).strip()
TVBOX_LIST_CFG = str(os.getenv("TVBOX_LIST_CFG", "")).strip()


async def add_tools(mcp: FastMCP, session: aiohttp.ClientSession, logger=None):

    if not (TVBOX_LOCAL_IP or TVBOX_LIST_CFG):
        return

    @mcp.tool(
        title="通过TvBox播放影视",
        description=f"在电视(投影仪/机顶盒)上播放远程影视URL，需要安装TvBox。\n{TVBOX_LIST_CFG}",
    )
    async def tvbox_play_media(
        url: str = Field(description="影视资源完整URL，如: m3u8/mp4 地址等"),
        addr: str = Field("", description="电视IP或Base URL"),
    ):
        if not url.strip():
            return {"error": "请输入影视资源URL"}
        if not addr.strip():
            addr = TVBOX_LOCAL_IP
        if not addr.startswith("http"):
            addr = f"http://{addr}:9978"
        else:
            addr = addr.rstrip("/")
        txt = None
        try:
            req = await session.post(
                f"{addr}/action",
                params={
                    "do": "push",
                    "url": url,
                },
                timeout=aiohttp.ClientTimeout(total=5),
            )
            txt = (await req.text()).strip()
            rdt = json.loads(txt) or {}
            if rdt:
                return {
                    "status_code": req.status,
                    **rdt,
                }
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            return {
                "error": str(exc),
                "addr": addr,
                "tip": "请确认电视已打开，并且TvBox已运行",
            }
        except json.decoder.JSONDecodeError:
            return {
                "text": txt,
                "addr": addr,
            }
        return {
            "status": req.reason if req else "Unknown",
            "text": txt,
            "addr": addr,
        }
