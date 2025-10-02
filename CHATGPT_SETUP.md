## ChatGPT Custom GPT Setup for Viterbit MCP

### Issue: ChatGPT Schema Validation

ChatGPT validates requests **client-side** against the OpenAPI schema before sending them to your server. If the schema is too strict, it will reject requests that don't match perfectly.

### Solution: Use the Simplified OpenAPI Schema

Copy this **exact** schema into your ChatGPT Custom GPT Action:

```yaml
openapi: 3.1.0
info:
  title: Viterbit MCP Server
  description: Access to Viterbit recruitment API
  version: 2.0.0

servers:
  - url: https://mcp-viterbit.onrender.com

paths:
  /tools/call:
    post:
      operationId: callTool
      summary: Execute a Viterbit tool
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object

components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

**Key Points:**
- `schema: type: object` with NO properties defined = accepts any JSON
- This lets ChatGPT send requests in any format
- Your server handles the parsing flexibly

### Setup Steps

1. **Go to ChatGPT** → My GPTs → Your Viterbit GPT

2. **Configure** → **Actions** → **Edit Action**

3. **Replace the entire schema** with the simple one above

4. **Update your server URL** in the schema:
   - Replace `https://mcp-viterbit.onrender.com` with your actual Render URL

5. **Authentication:**
   - Type: `API Key`
   - Header name: `X-API-Key`
   - Value: One of your `MCP_API_KEYS`

6. **Save**

### Custom GPT Instructions

Add these instructions to help ChatGPT format requests correctly:

```
You are a Viterbit recruitment assistant with access to the Viterbit API.

When calling tools:
- Use the callTool operation
- Send requests in this format: {"name": "tool_name", "arguments": {"param": "value"}}
- Available tools: search_candidate, get_candidate_details, update_candidate_discord_id, etc.
- Always check the result for success/error before responding to the user

Example tool call for searching a candidate:
{
  "name": "search_candidate",
  "arguments": {
    "email": "candidate@example.com"
  }
}

If a tool call fails, explain the error to the user clearly.
```

### Testing

Once configured, test with:

```
Search for candidate with email: fernandezporrasluisalberto@gmail.com
```

ChatGPT should call:
```json
{
  "name": "search_candidate",
  "arguments": {
    "email": "fernandezporrasluisalberto@gmail.com"
  }
}
```

### Troubleshooting

**Error: "Error al hablar con connector"**
- This means ChatGPT rejected the request CLIENT-SIDE
- The request never reached your server
- Fix: Use the simplified schema above

**Error: "Missing required parameter"**
- The request reached your server but parameters are missing
- Check ChatGPT's request format in the action logs
- The server expects either:
  - `{"name": "tool", "arguments": {"param": "val"}}`
  - OR `{"name": "tool", "param": "val"}`

**Error: "Invalid API key"**
- Check your X-API-Key matches one in `MCP_API_KEYS`
- Verify authentication is configured correctly in ChatGPT

### Alternative: List All Tools First

Add this tool to your OpenAPI schema to let ChatGPT discover available tools:

```yaml
  /tools:
    get:
      operationId: listTools
      summary: Get all available Viterbit tools
      security:
        - ApiKeyAuth: []
      responses:
        '200':
          description: List of tools with schemas
          content:
            application/json:
              schema:
                type: array
```

Then instruct ChatGPT:
```
At the start of each conversation, call listTools to see what's available.
```

### Server Logs

To debug, check your Render logs:
- Go to Render Dashboard
- Click your service
- Click "Logs"
- Look for:
  - `Raw request body: ...` (shows exactly what was sent)
  - `Tool called: ... with arguments: ...`
  - Any error messages

The server logs EVERYTHING for debugging.
