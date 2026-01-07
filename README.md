# 📺 MCP Server for Binge-watch

<!-- mcp-name: io.github.aahl/mcp-vods -->


## 📲 Install

### Method 1: uvx
```yaml
{
  "mcpServers": {
    "mcp-okx": {
      "command": "uvx",
      "args": ["mcp-vods"],
      "env": {
        "LUNA_BASE_URL": "your-lunaTV-base-url", # 别名: MOON_BASE_URL, 如: http://localhost:3000
        "LUNA_USERNAME": "your-lunaTV-username", # LunaTV 登录账号，可选
        "LUNA_PASSWORD": "your-lunaTV-password", # LunaTV 登录密码，可选
      }
    }
  }
}
```

### Method 2: Docker
```bash
mkdir /opt/mcp-okx
cd /opt/mcp-okx
wget https://raw.githubusercontent.com/aahl/mcp-okx/refs/heads/main/docker-compose.yml
docker-compose up -d
```
```yaml
{
  "mcpServers": {
    "mcp-okx": {
      "url": "http://0.0.0.0:8821/mcp" # Streamable HTTP
    }
  }
}
```


## 🔗 Links
- [LunaTV](https://github.com/MoonTechLab/LunaTV)
- [MoonTV](https://github.com/aahl/MoonTV)
