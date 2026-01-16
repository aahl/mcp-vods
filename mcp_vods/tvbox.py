import os
import json
import requests
from fastmcp import FastMCP
from pydantic import Field

TVBOX_LOCAL_IP = str(os.getenv("TVBOX_LOCAL_IP", "")).strip()
TVBOX_LIST_CFG = str(os.getenv("TVBOX_LIST_CFG", "")).strip()


def add_tools(mcp: FastMCP, logger=None):

    if not (TVBOX_LOCAL_IP or TVBOX_LIST_CFG):
        return

    @mcp.tool(
        title="通过TvBox播放影视",
        description=f"在电视(投影仪/机顶盒)上播放远程影视URL，需要安装TvBox。\n{TVBOX_LIST_CFG}",
    )
    def tvbox_play_media(
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
        req = None
        try:
            req = requests.post(
                f"{addr}/action",
                params={
                    "do": "push",
                    "url": url,
                },
                timeout=5,
            )
            rdt = json.loads(req.text.strip()) or {}
            if rdt:
                return {
                    "status_code": req.status_code,
                    **rdt,
                }
        except requests.exceptions.RequestException as exc:
            return {
                "error": str(exc),
                "addr": addr,
                "tip": "请确认电视已打开，并且TvBox已运行",
            }
        except json.decoder.JSONDecodeError:
            return {
                "text": req.text,
                "addr": addr,
            }
        return {
            "status": req.reason if req else "Unknown",
            "text": req.text if req else None,
            "addr": addr,
        }
