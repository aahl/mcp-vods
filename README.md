# 📺 MCP Server for Binge-watch

<!-- mcp-name: io.github.aahl/mcp-vods -->

一个用于追剧/追番的MCP服务器，为AI提供搜索影视播放地址的能力，并支持在小米电视上直接播放。


## 📲 安装

### 方式1: uvx
```yaml
{
  "mcpServers": {
    "vods": {
      "command": "uvx",
      "args": ["mcp-vods"],
      "env": {
        "MITV_LIST_CFG": "客厅电视:192.168.1.11"
      }
    }
  }
}
```

### 方式2: Docker
```bash
mkdir /opt/mcp-vods
cd /opt/mcp-vods
wget https://raw.githubusercontent.com/aahl/mcp-vods/refs/heads/main/docker-compose.yml
docker-compose up -d
```
```yaml
{
  "mcpServers": {
    "vods": {
      "url": "http://0.0.0.0:8821/mcp" # Streamable HTTP
    }
  }
}
```

### 方式3: Home Assistant OS [Add-on](https://gitee.com/hasscc/addons/tree/main/mcp-vods)
[![添加加载项仓库](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgitee.com%2Fhasscc%2Faddons)


### 快速开始
- 添加到 Claude Code, 执行命令:
  - `claude mcp add vods -- uvx mcp-vods`
  - `claude mcp add vods --env MITV_LIST_CFG=客厅电视:192.168.1.11 -- uvx mcp-vods`
- 添加到 OpenAI CodeX, 执行命令: `codex mcp add vods -- uvx mcp-vods`
- 添加到 Cursor [![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/zh/install-mcp?name=vods&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtY3Atdm9kcyJdfQ==)
- 添加到 VS Code [![Install MCP Server](https://img.shields.io/badge/VS_Code-+?label=Add+MCP+Server&color=0098FF)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install%3F%7B%22name%22%3A%22vods%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-vods%22%5D%7D)
- 添加到 Cherry Studio [![Install MCP Server](https://img.shields.io/badge/Cherry_Studio-+?label=Add+MCP+Server&color=FF5F5F)](https://gitee.com/link?target=cherrystudio%3A%2F%2Fmcp%2Finstall%3Fservers%3DeyJtY3BTZXJ2ZXJzIjp7InZvZHMiOnsiY29tbWFuZCI6InV2eCIsImFyZ3MiOlsibWNwLXZvZHMiXX19fQ%3D%3D)


### ⚙️ 环境变量

#### 免配置开箱即用
- `VOD_CONFIG_URL`: LunaTV/MoonTV订阅源[远程配置文件](https://github.com/hafrey1/LunaTV-config)URL，可选(默认已内置)
- `SEARCH_CACHE_TTL`: 搜索缓存TTL，可选(默认5分钟)
- `MAX_SEARCH_SITES`: 单次最多搜索站点数，可选(默认10)

#### 使用已部署的LunaTV/MoonTV
- `MOON_BASE_URL`: 已部署的MoonTV服务地址，可选，如: `http://0.0.0.0:3000`
- `LUNA_BASE_URL`: 已部署的LunaTV服务地址，可选
- `LUNA_USERNAME`: LunaTV 登录账号，可选
- `LUNA_PASSWORD`: LunaTV 登录密码，可选

#### 小米电视/投影/机顶盒
> 如需在小米电视上播放视频，要至少配置`MITV_LOCAL_IP`或`MITV_LIST_CFG`之一

- `MITV_LOCAL_IP`: 单台小米电视本地IP，可选
- `MITV_LIST_CFG`: 多台小米电视配置，可选，如: `客厅电视:192.168.1.11;主卧电视:192.168.1.12`

#### 其他安卓电视/投影/机顶盒
> 如需在非小米安卓电视上播放视频，需要安装[TvBox](https://github.com/o0HalfLife0o/TVBoxOSC/releases)，并至少配置`TVBOX_LOCAL_IP`或`TVBOX_LIST_CFG`之一

- `TVBOX_LOCAL_IP`: 单台电视本地IP，可选
- `TVBOX_LIST_CFG`: 多台电视配置，可选，如: `客厅电视:192.168.1.11;主卧电视:192.168.1.12`


## 🔗 Links
- https://zread.ai/aahl/mcp-vods
- [LunaTV](https://github.com/MoonTechLab/LunaTV)
- [MoonTV](https://github.com/aahl/MoonTV)
