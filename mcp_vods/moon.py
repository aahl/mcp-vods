import os
import yaml
import requests
from fastmcp import FastMCP
from pydantic import Field

MOON_BASE_URL = str(os.getenv("MOON_BASE_URL", "") or os.getenv("LUNA_BASE_URL", "")).rstrip("/")


def add_tools(mcp: FastMCP):

    SESSION = requests.session()

    if not MOON_BASE_URL:
        @mcp.tool(
            title="MoonTV/LunaTV地址未配置提示",
            description="MoonTV/LunaTV地址未配置提示",
        )
        def moon_warning():
            return "MoonTV/LunaTV地址未配置，请配置`MOON_BASE_URL`环境变量"
        return

    if pwd := os.getenv("LUNA_PASSWORD"):
        SESSION.post(
            f"{MOON_BASE_URL}/api/login",
            json={
                "username": os.getenv("LUNA_USERNAME", ""),
                "password": pwd,
            },
        )

    @mcp.tool(
        title="搜索影视",
        description="搜索电影、电视剧、综艺节目、动漫、番剧、短剧等。\n"
                    "你可以说:\n"
                    "- 我想看仙逆最新一集\n"
                    "- 凡人修仙传更新到多少集了\n",
    )
    def moon_search(
        keyword: str = Field(description="搜索关键词，如电影名称"),
    ):
        resp = SESSION.get(
            f"{MOON_BASE_URL}/api/search",
            params={
                "q": keyword,
            },
        )
        try:
            data = resp.json() or {}
        except Exception as exc:
            return {"text": resp.text(), "error": str(exc)}
        results = data.get("results", [])
        for item in results:
            episodes = item.pop("episodes") or []
            episodes = dict(zip(range(1, len(episodes) + 1), episodes))
            item.update({
                "episodes_count": len(episodes),
                "episodes_newest": dict(list(episodes.items())[-3:]),
            })
        return yaml.dump(results or data, allow_unicode=True)

    @mcp.tool(
        title="影视详情",
        description="获取电影、电视剧、综艺节目、动漫、番剧、短剧等节目的详情及播放地址",
    )
    def moon_detail(
        id: str = Field(description="影视节目ID，可通过搜索工具(moon_search)获取"),
        source: str = Field(description="数据来源(source)"),
        episode: int = Field(0, description="剧集(第N集)，获取最新一集传`0`，获取全部剧集传`-1`"),
    ):
        resp = SESSION.get(
            f"{MOON_BASE_URL}/api/detail",
            params={
                "source": source,
                "id": id,
            },
        )
        try:
            data = resp.json() or {}
        except Exception as exc:
            return {"text": resp.text(), "error": str(exc)}
        episode = int(episode)
        episodes = data.get("episodes") or []
        episodes = dict(zip(range(1, len(episodes) + 1), episodes))
        if episode >= 0:
            if episode == 0:
                episode = list(episodes.keys())[-1]
            if url := episodes.get(episode):
                data.pop("episodes", None)
                data.update({
                    "play_url": url,
                    "episodes_newest": dict(list(episodes.items())[-3:]),
                })
            else:
                data.update({
                    "play_url": f"剧集[{episode}]未找到",
                })
        if "episodes" in data:
            data.update({
                "episodes": episodes,
            })
        return yaml.dump(data, allow_unicode=True)
