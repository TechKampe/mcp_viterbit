# Viterbit MCP Server - HTTP/SSE Edition

A Model Context Protocol (MCP) server that provides remote access to Viterbit recruitment API functionality via HTTP and Server-Sent Events (SSE).

## 🚀 What's New in HTTP/SSE Version

This version enables **remote access** to your Viterbit MCP server, allowing:
- ✅ Third-party access over the internet
- ✅ Multiple clients connecting simultaneously
- ✅ API key authentication
- ✅ Easy deployment to cloud platforms
- ✅ RESTful API endpoints
- ✅ Real-time updates via SSE

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Deployment Options](#deployment-options)
- [API Documentation](#api-documentation)
- [Client Integration](#client-integration)
- [Security](#security)

## Quick Start

### 1. Install Dependencies

```bash
cd mcp_viterbit
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set:
# - VITERBIT_API_KEY (required)
# - MCP_API_KEYS (comma-separated client API keys)
```

### 3. Run the Server

```bash
python server_http.py
```

Server will start on `http://localhost:8000`

### 4. Test the Server

```bash
# Health check
curl http://localhost:8000/health

# List tools (requires authentication)
curl -H "X-API-Key: your_key_here" http://localhost:8000/tools
```

## Local Development

### Running with Uvicorn

```bash
# Development mode with auto-reload
uvicorn server_http:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn server_http:app --host 0.0.0.0 --port 8000 --workers 4
```

### Running with Docker

```bash
# Build the image
docker build -t viterbit-mcp .

# Run the container
docker run -p 8000:8000 --env-file .env viterbit-mcp
```

### Running with Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Deployment Options

### Option 1: Render.com (Recommended)

1. **Push your code to GitHub**
2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your repository
3. **Configure:**
   - Render will auto-detect `render.yaml`
   - Add environment variables:
     - `VITERBIT_API_KEY`
     - `MCP_API_KEYS`
4. **Deploy!**

Your server will be available at: `https://your-app-name.onrender.com`

### Option 2: Railway.app

1. **Push your code to GitHub**
2. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
3. **Set environment variables:**
   - `VITERBIT_API_KEY`
   - `MCP_API_KEYS`
4. **Deploy!**

Railway will automatically detect `railway.json` and deploy.

### Option 3: AWS/Google Cloud/Azure

Deploy using Docker:

```bash
# Build for production
docker build -t viterbit-mcp:latest .

# Tag for your registry
docker tag viterbit-mcp:latest your-registry/viterbit-mcp:latest

# Push to registry
docker push your-registry/viterbit-mcp:latest

# Deploy to your cloud provider
# (Use their container services: ECS, Cloud Run, Container Apps)
```

### Option 4: VPS (DigitalOcean, Linode, etc.)

```bash
# On your VPS:
git clone your-repo
cd mcp_viterbit

# Set up environment
cp .env.example .env
nano .env  # Edit with your keys

# Install dependencies
pip install -r requirements.txt

# Run with systemd (recommended)
sudo nano /etc/systemd/system/viterbit-mcp.service
```

**systemd service file:**
```ini
[Unit]
Description=Viterbit MCP HTTP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/mcp_viterbit
Environment="PATH=/path/to/mcp_viterbit/.venv/bin"
EnvironmentFile=/path/to/mcp_viterbit/.env
ExecStart=/path/to/mcp_viterbit/.venv/bin/python -m uvicorn server_http:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable viterbit-mcp
sudo systemctl start viterbit-mcp
```

## API Documentation

### Base URL
- Local: `http://localhost:8000`
- Production: `https://your-domain.com`

### Authentication
All endpoints (except `/health` and `/`) require authentication via `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" https://your-domain.com/tools
```

### Endpoints

#### `GET /` - Server Information
Returns basic server info and available endpoints.

**Response:**
```json
{
  "name": "Viterbit MCP Server",
  "version": "2.0.0",
  "protocol": "HTTP/SSE",
  "endpoints": { ... },
  "documentation": "/docs"
}
```

#### `GET /health` - Health Check
Check server status (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "tools_count": 16
}
```

#### `GET /tools` - List Available Tools
Get all MCP tools with their schemas.

**Headers:**
```
X-API-Key: your_api_key
```

**Response:**
```json
[
  {
    "name": "search_candidate",
    "description": "Search for a candidate by email",
    "inputSchema": { ... }
  },
  ...
]
```

#### `POST /tools/call` - Execute a Tool
Call a specific MCP tool.

**Headers:**
```
X-API-Key: your_api_key
Content-Type: application/json
```

**Request:**
```json
{
  "name": "search_candidate",
  "arguments": {
    "email": "john@example.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": [ ... ],
  "error": null
}
```

#### `GET /sse` - Server-Sent Events Stream
Real-time event stream for updates.

**Headers:**
```
X-API-Key: your_api_key
```

**Events:**
- `connected` - Initial connection established
- `tools` - Available tools list
- `ping` - Keepalive (every 30s)

#### `GET /docs` - Interactive API Documentation
FastAPI auto-generated Swagger UI documentation.

## Client Integration

### Claude Desktop Integration

Update your Claude Desktop configuration to use the HTTP server:

```json
{
  "mcpServers": {
    "viterbit": {
      "url": "https://your-domain.com",
      "headers": {
        "X-API-Key": "your_client_api_key"
      },
      "transport": "sse"
    }
  }
}
```

### Python Client Example

```python
import httpx

BASE_URL = "https://your-domain.com"
API_KEY = "your_api_key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# List tools
response = httpx.get(f"{BASE_URL}/tools", headers=headers)
tools = response.json()

# Call a tool
response = httpx.post(
    f"{BASE_URL}/tools/call",
    headers=headers,
    json={
        "name": "search_candidate",
        "arguments": {"email": "test@example.com"}
    }
)
result = response.json()
print(result)
```

### JavaScript/TypeScript Client Example

```typescript
const BASE_URL = 'https://your-domain.com';
const API_KEY = 'your_api_key';

// List tools
const tools = await fetch(`${BASE_URL}/tools`, {
  headers: {
    'X-API-Key': API_KEY
  }
}).then(r => r.json());

// Call a tool
const result = await fetch(`${BASE_URL}/tools/call`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'search_candidate',
    arguments: { email: 'test@example.com' }
  })
}).then(r => r.json());
```

### cURL Examples

```bash
# List all tools
curl -H "X-API-Key: your_key" \
  https://your-domain.com/tools

# Search for a candidate
curl -X POST \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"name":"search_candidate","arguments":{"email":"test@example.com"}}' \
  https://your-domain.com/tools/call

# Get candidate count
curl -X POST \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"name":"get_candidate_count","arguments":{"is_subscriber":true}}' \
  https://your-domain.com/tools/call
```

## Security

### Authentication Setup

1. **Generate strong API keys:**
```bash
# Generate random keys (example)
python -c "import secrets; print(','.join([secrets.token_urlsafe(32) for _ in range(3)]))"
```

2. **Set in environment:**
```bash
MCP_API_KEYS=key1,key2,key3
```

3. **Distribute to clients securely**

### Best Practices

✅ **DO:**
- Use HTTPS in production (handled automatically by Render/Railway)
- Rotate API keys regularly
- Use separate keys for different clients
- Monitor access logs
- Set `ALLOWED_ORIGINS` to specific domains in production
- Use strong, randomly generated API keys

❌ **DON'T:**
- Commit `.env` file to git
- Share API keys in public channels
- Use weak or predictable API keys
- Leave `MCP_API_KEYS` empty in production
- Use `ALLOWED_ORIGINS=*` in production

### CORS Configuration

For production, restrict origins:

```bash
ALLOWED_ORIGINS=https://app1.example.com,https://app2.example.com
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITERBIT_API_KEY` | ✅ Yes | - | Your Viterbit API key |
| `MCP_API_KEYS` | ⚠️ Recommended | - | Comma-separated client API keys |
| `PORT` | No | `8000` | Server port |
| `HOST` | No | `0.0.0.0` | Server host |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins |

## Monitoring & Logs

### Check Server Status

```bash
# Health check
curl https://your-domain.com/health

# Detailed status
curl https://your-domain.com/
```

### View Logs

**Local:**
```bash
# Server logs are printed to stdout
python server_http.py
```

**Docker:**
```bash
docker-compose logs -f
```

**Render/Railway:**
- Check the web dashboard for live logs

## Troubleshooting

### Issue: "Invalid API key"
**Solution:** Verify `X-API-Key` header matches a key in `MCP_API_KEYS`

### Issue: "VITERBIT_API_KEY is required"
**Solution:** Set `VITERBIT_API_KEY` in environment or `.env` file

### Issue: CORS errors
**Solution:** Update `ALLOWED_ORIGINS` to include your client domain

### Issue: Connection timeout
**Solution:** Check firewall, ensure port is exposed, verify health endpoint

### Issue: 503 Server not initialized
**Solution:** Check logs for startup errors, verify Viterbit API key is valid

## Migration from stdio Version

If you're upgrading from the original stdio-based server:

1. **Keep original server:** [server.py](server.py) still works for local Claude Desktop
2. **New HTTP server:** Use [server_http.py](server_http.py) for remote access
3. **Choose based on needs:**
   - Local only → Use `server.py`
   - Remote access → Use `server_http.py`
   - Both → Run both on different ports

## Available Tools

All 16 tools from the original version are available:

### Candidate Management
- `search_candidate`
- `get_candidate_details`
- `get_candidate_with_filters`
- `update_candidate_discord_id`
- `update_candidate_subscription`
- `update_candidate_stage`
- `search_subscribers`
- `get_candidate_count`

### Job Management
- `get_job_details`

### Candidature Management
- `find_active_candidatures`
- `disqualify_candidature`
- `disqualify_all_candidatures`

### Utility Tools
- `get_custom_fields_definitions`
- `check_candidate_eligibility`
- `get_department_location_mappings`
- `extract_discord_username`

## License

Generated with Claude Code for Viterbit recruitment systems.

## Support

- 📖 API Docs: `https://your-domain.com/docs`
- 🏥 Health Check: `https://your-domain.com/health`
- 📊 Server Info: `https://your-domain.com/`
