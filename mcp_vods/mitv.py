import os
import time
import json
import hashlib
import requests
from fastmcp import FastMCP
from pydantic import Field

MITV_LOCAL_IP = str(os.getenv("MITV_LOCAL_IP", "")).strip()
MITV_LIST_CFG = str(os.getenv("MITV_LIST_CFG", "")).strip()
MITV_API_KEY = os.getenv("MITV_API_KEY", "881fd5a8c94b4945b46527b07eca2431")


def add_tools(mcp: FastMCP, logger=None):

    if not (MITV_LOCAL_IP or MITV_LIST_CFG):
        return

    @mcp.tool(
        title="在小米电视上播放影视",
        description=f"在小米电视(投影仪/机顶盒)上播放远程影视URL。\n{MITV_LIST_CFG}",
    )
    def mitv_play_media(
        url: str = Field(description="影视资源完整URL，如: m3u8/mp4 地址等"),
        addr: str = Field("", description="小米电视IP或Base URL"),
    ):
        if not url.strip():
            return {"error": "请输入影视资源URL"}
        if not addr.strip():
            addr = MITV_LOCAL_IP
        if not addr.startswith("http"):
            addr = f"http://{addr}:6095"
        else:
            addr = addr.rstrip("/")
        tim = str(int(time.time() * 1000))
        pms = {
            "action": "play",
            "type": "video",
            "url": url,
            "ts": tim,
            "apikey": MITV_API_KEY,
            "sign": hashlib.md5(f"mitvsignsalt{url}{MITV_API_KEY}{tim[-5:]}".encode()).hexdigest(),
        }
        req = None
        try:
            req = requests.get(
                f"{addr}/controller",
                params=pms,
                timeout=10,
            )
            rdt = json.loads(req.text.split()) or {}
            return rdt
        except requests.exceptions.RequestException as exc:
            return {
                "error": str(exc),
                "addr": addr,
                "tip": "请确认电视是打开状态",
            }
        except json.decoder.JSONDecodeError:
            return {
                "text": req.text,
                "addr": addr,
            }
        finally:
            return {
                "status": req.reason if req else "Unknown",
                "addr": addr,
            }
