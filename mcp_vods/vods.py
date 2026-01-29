import os
import io
import re
import csv
import json
import yaml
import aiohttp
from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from pydantic import Field
from functools import cached_property
from cachetools import TTLCache

DFL_CONFIG_URL = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/jin18.json"
VOD_CONFIG_URL = os.getenv("VOD_CONFIG_URL", DFL_CONFIG_URL)
VOD_API_TIMEOUT = int(os.getenv("VOD_API_TIMEOUT", 7))
SEARCH_CACHE_TTL = int(os.getenv("SEARCH_CACHE_TTL", 300))
MAX_SEARCH_SITES = int(os.getenv("MAX_SEARCH_SITES", 10))

CACHE_STORE = TTLCache(maxsize=2000, ttl=SEARCH_CACHE_TTL)


async def add_tools(mcp: FastMCP, session: aiohttp.ClientSession, logger=None):

    if not VOD_CONFIG_URL:
        logger.error("Config URL is empty !")
        return

    CONFIGS = {}
    GH_PROXYS = [
        "https://ghfast.top/raw.githubusercontent.com",
        "https://gh-proxy.com/raw.githubusercontent.com",
        "https://cfrp.hacs.vip/raw.githubusercontent.com",
        "https://raw.githubusercontent.com",
    ]
    for proxy in GH_PROXYS:
        try:
            async with session.get(
                VOD_CONFIG_URL.replace("https://raw.githubusercontent.com", proxy),
                timeout=aiohttp.ClientTimeout(total=VOD_API_TIMEOUT),
            ) as resp:
                if resp.status == 200:
                    CONFIGS = json.loads((await resp.text()).strip()) or {}
            if CONFIGS:
                logger.info("Loaded configs from %s", VOD_CONFIG_URL)
                break
        except Exception:
            logger.error("Failed to load configs from %s", proxy, exc_info=True)
    if not CONFIGS:
        logger.error("Failed to load configs from %s", VOD_CONFIG_URL)
        return

    @mcp.tool(
        title="搜索影视",
        description="搜索电影、电视剧、综艺节目、动漫、番剧、短剧等。如果超时可多重试几次。\n"
                    "当用户说以下内容时可通过本工具搜索资源:\n"
                    "- 我想看《仙逆》最新一集\n"
                    "- 凡人修仙传更新到多少集了\n",
    )
    async def vods_search(
        keyword: str = Field(description="搜索关键词，如电影名称，不要包含书名号、引号等"),
    ):
        results = []
        queries = 0
        apis = CONFIGS.get("api_site") or {}
        for source, cfg in apis.items():
            key = f"search-{source}-{keyword}"
            if key in CACHE_STORE:
                results.extend(CACHE_STORE[key])
                logger.info("Cache hit: %s", [source, keyword])
                continue

            queries += 1
            lst = await vod_search_by_source(source, keyword)
            CACHE_STORE[key] = lst
            results.extend(lst)
            if queries >= MAX_SEARCH_SITES:
                break
        if not results:
            return "未找到相关结果"

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(results[0].keys()))
        writer.writeheader()
        for item in results:
            writer.writerow(item)
        text = output.getvalue()
        output.close()
        return ToolResult(content=text)

    @mcp.tool(
        title="影视详情",
        description="获取电影、电视剧、综艺节目、动漫、番剧、短剧等节目的详情及播放地址",
    )
    async def vods_detail(
        id: str = Field(description="影视节目ID，可通过搜索工具(vod_search)获取"),
        source: str = Field(description="数据来源(source)"),
        episode: int = Field(0, description="剧集(第N集)，获取最新一集传`0`，获取全部剧集传`-1`"),
    ):
        cfg = CONFIGS.get("api_site", {}).get(source)
        if not cfg:
            return {"text": f"数据源{source}不存在"}
        async with session.get(
            cfg.get("api"),
            params={
                "ac": "videolist",
                "ids": id,
            },
        ) as resp:
            try:
                data = json.loads((await resp.text()).strip()) or {}
            except Exception as exc:
                return {"text": await resp.text(), "error": str(exc)}
        lst = data.get("list", [])
        if not lst:
            return {"text": f"ID[{id}]未找到"}
        vod = Vod(lst[0])
        data = vod.format()
        data.update({
            "episodes": vod.episodes,
        })
        if episode >= 0:
            url = vod.episode_play_url(episode)
            if url:
                data.pop("episodes", None)
                data.update({
                    "play_url": url,
                    "episodes_newest": vod.episodes_newest(),
                })
            else:
                data.update({
                    "play_url": f"剧集[{episode}]未找到",
                })
        return ToolResult(
            content=yaml.dump(data, allow_unicode=True, sort_keys=False),
            structured_content=data,
        )

    async def vod_search_by_source(source, keyword):
        results = []
        cfg = CONFIGS.get("api_site", {}).get(source)
        if not cfg:
            return results
        try:
            async with session.get(
                cfg.get("api"),
                params={
                    "ac": "videolist",
                    "wd": keyword,
                },
                timeout=aiohttp.ClientTimeout(total=VOD_API_TIMEOUT),
            ) as resp:
                data = json.loads((await resp.text()).strip()) or {}
        except Exception as exc:
            logger.error("Failed search video via %s: %s", source, exc)
            return results
        lst = data.get("list", [])
        for item in lst:
            vod = Vod(item)
            if not vod.episode_list:
                logger.warning("No episode list via %s: %s", source, vod.format())
                continue
            episodes = vod.episodes_newest(1)
            results.append({
                "id": vod.id,
                "source": source,
                "source_name": cfg.get("name") or source,
                "episodes_newest": episodes[-1] if episodes else "",
                **vod.format(),
            })
        return results


class Vod(dict):
    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = Vod(value) if isinstance(value, dict) else value

    @cached_property
    def episodes(self):
        return [
            f"{x['url']}#{x['label']}"
            for x in self.episode_list
        ]

    @cached_property
    def episode_dict(self):
        return {
            x['label']: x['url']
            for x in self.episode_list
        }

    @cached_property
    def episode_list(self):
        return [
            {"label": a[0], "url": a[1]}
            for x in self.get("vod_play_url", "").split("$$$")[0].split("#")
            if len(a := x.split("$")) > 1
        ]

    def episodes_newest(self, count=3):
        return self.episodes[-count:]

    def episode_play_url(self, episode):
        episodes = self.episodes
        if episode == 0 and episodes:
            return episodes[-1]
        try:
            epn = int(episode)
            if epn <= len(episodes):
                return episodes[epn - 1]
        except Exception:
            pass
        return self.episode_dict.get(str(episode))

    def format(self):
        intro = re.sub(r'<[^>]+>', '', str(self.vod_blurb)).strip()
        desc = re.sub(r'<[^>]+>', '', str(self.vod_content)).strip()
        if intro and intro in desc:
            intro = ""
        return {
            "id": self.vod_id,
            "title": self.vod_name,
            "year": self.vod_year,
            "remark": self.vod_remarks,
            "type_name": self.type_name,
            "update_at": self.vod_time,
            "episodes_count": len(self.episodes),
            "poster": self.vod_pic,
            "intro": intro,
            "desc": desc,
        }
