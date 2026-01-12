# 📺 MCP Server for Binge-watch

<!-- mcp-name: io.github.aahl/mcp-vods -->


## 📲 Install

### Method 1: uvx
```yaml
{
  "mcpServers": {
    "mcp-vods": {
      "command": "uvx",
      "args": ["mcp-vods"],
      "env": {
        "SEARCH_CACHE_TTL": "5"
      }
    }
  }
}
```

### Method 2: Docker
```bash
mkdir /opt/mcp-vods
cd /opt/mcp-vods
wget https://raw.githubusercontent.com/aahl/mcp-vods/refs/heads/main/docker-compose.yml
docker-compose up -d
```
```yaml
{
  "mcpServers": {
    "mcp-vods": {
      "url": "http://0.0.0.0:8821/mcp" # Streamable HTTP
    }
  }
}
```


### ⚙️ 环境变量

#### 免配置开箱即用
- `VOD_CONFIG_URL`: [远程配置文件](https://github.com/hafrey1/LunaTV-config)URL，可选(默认已内置)
- `SEARCH_CACHE_TTL`: 搜索缓存TTL，可选(默认5分钟)
- `MAX_SEARCH_SITES`: 搜索次数限制，可选(默认10)

#### 使用已部署的LunaTV/MoonTV
- `MOON_BASE_URL`: 已部署的MoonTV服务地址，可选，如: http://localhost:3000
- `LUNA_BASE_URL`: 已部署的LunaTV服务地址，可选
- `LUNA_USERNAME`: LunaTV 登录账号，可选
- `LUNA_PASSWORD`: LunaTV 登录密码，可选


## 🔗 Links
- [LunaTV](https://github.com/MoonTechLab/LunaTV)
- [MoonTV](https://github.com/aahl/MoonTV)
